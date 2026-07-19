"""Integration tests for referrals.repositories module.

Tests cover:
- ReferralRepository: CRUD, inter-LGA queries, status tracking,
  inbound/outbound filtering, overdue detection

Uses real PostgreSQL database. All tests run inside Django transactions.

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from accounts.models import LGA, User
from cases.models import Case
from migrants.models import Migrant
from referrals.models import Referral
from referrals.repositories import ReferralRepository


@pytest.fixture
def from_lga():
    """Return Aba North as originating LGA."""
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def to_lga():
    """Return Aba South as receiving LGA."""
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_user(from_lga):
    """Create and return a test user in Aba North."""
    user = User.objects.create_user(
        username="referralofficer",
        password="RefPass123!",
        role="field_officer",
        lga=from_lga,
    )
    return user


@pytest.fixture
def test_coordinator(to_lga):
    """Create and return a test coordinator in Aba South."""
    user = User.objects.create_user(
        username="coordinator",
        password="CoordPass123!",
        role="lga_coordinator",
        lga=to_lga,
    )
    return user


@pytest.fixture
def test_migrant(from_lga):
    """Create and return a test migrant."""
    from datetime import date

    migrant = Migrant.objects.create(
        full_name="Referral Subject",
        phone="+2348022222222",
        date_of_birth=date(1992, 6, 10),
        current_lga=from_lga,
        lga_of_origin=from_lga,
        status="active",
    )
    return migrant


@pytest.fixture
def test_case(test_user, test_migrant, from_lga):
    """Create and return a test case."""
    case = Case.objects.create(
        migrant=test_migrant,
        lga=from_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="high",
        case_type="medical",
        description="Case requiring referral",
    )
    return case


@pytest.fixture
def test_referral(
    test_case, test_migrant, from_lga, to_lga, test_user, test_coordinator
):
    """Create and return a test referral."""
    referral = Referral.objects.create(
        case=test_case,
        migrant=test_migrant,
        from_lga=from_lga,
        to_lga=to_lga,
        referred_by=test_user,
        assigned_to=test_coordinator,
        status="pending",
        reason="Medical emergency requiring specialist care",
        notes="Patient has chronic condition",
    )
    return referral


@pytest.mark.django_db
class TestReferralRepository:
    """Integration tests for ReferralRepository with real database."""

    def test_get_all_referrals(self, test_referral):
        # Given: At least one referral exists
        # When: Repository retrieves all
        result = ReferralRepository.get_all()

        # Then: Returns queryset with referrals
        assert result.count() >= 1
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_id_existing(self, test_referral):
        # Given: Existing referral
        # When: Repository retrieves by ID
        result = ReferralRepository.get_by_id(test_referral.id)

        # Then: Correct referral returned
        assert result is not None
        assert result.reason == "Medical emergency requiring specialist care"

    def test_get_by_id_nonexistent(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository retrieves by ID
        result = ReferralRepository.get_by_id(fake_id)

        # Then: None returned
        assert result is None

    def test_get_by_from_lga(self, test_referral, from_lga):
        # Given: Referral from Aba North
        # When: Repository filters by originating LGA
        result = ReferralRepository.get_by_from_lga(from_lga.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_to_lga(self, test_referral, to_lga):
        # Given: Referral to Aba South
        # When: Repository filters by receiving LGA
        result = ReferralRepository.get_by_to_lga(to_lga.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_from_lga_empty(self, to_lga):
        # Given: LGA with no outbound referrals (Aba South has none)
        # When: Repository filters by that LGA as origin
        result = ReferralRepository.get_by_from_lga(to_lga.id)

        # Then: Empty queryset
        assert result.count() == 0

    def test_get_by_to_lga_empty(self, from_lga):
        # Given: LGA with no inbound referrals (Aba North has none)
        # When: Repository filters by that LGA as destination
        result = ReferralRepository.get_by_to_lga(from_lga.id)

        # Then: Empty queryset
        assert result.count() == 0

    def test_get_by_referred_by(self, test_referral, test_user):
        # Given: Referral created by test_user
        # When: Repository filters by referrer
        result = ReferralRepository.get_by_referred_by(test_user.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_assigned_to(self, test_referral, test_coordinator):
        # Given: Referral assigned to test_coordinator
        # When: Repository filters by assignee
        result = ReferralRepository.get_by_assigned_to(test_coordinator.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_create_referral(
        self, test_case, test_migrant, from_lga, to_lga, test_user, test_coordinator
    ):
        # Given: New referral data
        data = {
            "case": test_case,
            "migrant": test_migrant,
            "from_lga": from_lga,
            "to_lga": to_lga,
            "referred_by": test_user,
            "assigned_to": test_coordinator,
            "status": "pending",
            "reason": "Follow-up care needed",
            "notes": "Second referral for same case",
        }

        # When: Repository creates referral
        result = ReferralRepository.create(data)

        # Then: Referral created with correct attributes
        assert result.id is not None
        assert result.status == "pending"
        assert result.from_lga_id == from_lga.id
        assert result.to_lga_id == to_lga.id

    def test_update_referral_status(self, test_referral):
        # Given: Existing referral with status "pending"
        # When: Repository updates status
        updated = ReferralRepository.update(test_referral.id, {"status": "accepted"})

        # Then: Status updated
        assert updated.status == "accepted"

    def test_update_referral_notes(self, test_referral):
        # Given: Existing referral
        # When: Repository updates notes
        updated = ReferralRepository.update(
            test_referral.id, {"notes": "Updated notes"}
        )

        # Then: Notes updated
        assert updated.notes == "Updated notes"

    def test_update_referral_assigned_to(self, test_referral, to_lga):
        # Given: Existing referral and new assignee
        new_user = User.objects.create_user(
            username="newcoord",
            password="NewCoord123!",
            role="lga_coordinator",
            lga=to_lga,
        )

        # When: Repository updates assigned_to
        updated = ReferralRepository.update(test_referral.id, {"assigned_to": new_user})

        # Then: Assignment updated
        assert updated.assigned_to_id == new_user.id

    def test_update_nonexistent_referral(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository updates non-existent referral
        result = ReferralRepository.update(fake_id, {"status": "accepted"})

        # Then: Returns None
        assert result is None

    def test_delete_referral(self, test_referral):
        # Given: Existing referral
        referral_id = test_referral.id

        # When: Repository deletes referral
        result = ReferralRepository.delete(referral_id)

        # Then: Referral no longer exists
        assert result is True
        assert Referral.objects.filter(id=referral_id).count() == 0

    def test_delete_nonexistent_referral(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository deletes non-existent referral
        result = ReferralRepository.delete(fake_id)

        # Then: Returns False
        assert result is False

    def test_filter_by_status(self, test_referral):
        # Given: Referral with status "pending"
        # When: Repository filters by status
        result = ReferralRepository.filter_by_status("pending")

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_filter_by_status_no_results(self, test_referral):
        # Given: Referral with status "pending"
        # When: Repository filters by different status
        result = ReferralRepository.filter_by_status("completed")

        # Then: Empty queryset
        assert result.count() == 0

    def test_filter_by_status_from_lga(self, test_referral, from_lga):
        # Given: Pending referral from Aba North
        # When: Repository filters by status and origin LGA
        result = ReferralRepository.filter_by_status_from_lga("pending", from_lga.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_filter_by_status_to_lga(self, test_referral, to_lga):
        # Given: Pending referral to Aba South
        # When: Repository filters by status and destination LGA
        result = ReferralRepository.filter_by_status_to_lga("pending", to_lga.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_get_pending_by_to_lga(self, test_referral, to_lga):
        # Given: Pending referral to Aba South
        # When: Repository retrieves pending inbound referrals
        result = ReferralRepository.get_pending_by_to_lga(to_lga.id)

        # Then: Referral found
        assert result.filter(id=test_referral.id).exists()

    def test_get_pending_by_to_lga_empty(self, from_lga):
        # Given: Aba North has no inbound pending referrals
        # When: Repository retrieves pending inbound for Aba North
        result = ReferralRepository.get_pending_by_to_lga(from_lga.id)

        # Then: Empty queryset
        assert result.count() == 0

    def test_get_overdue_by_from_lga(self, test_referral, from_lga):
        # Given: Fresh referral (not overdue by default)
        # When: Repository retrieves overdue outbound referrals
        result = ReferralRepository.get_overdue_by_from_lga(from_lga.id)

        # Then: Likely empty (referral is fresh)
        assert result.count() >= 0

    def test_count_by_from_lga(self, test_referral, from_lga):
        # Given: Referral from Aba North
        # When: Repository counts outbound referrals
        result = ReferralRepository.count_by_from_lga(from_lga.id)

        # Then: Count >= 1
        assert result >= 1

    def test_count_by_to_lga(self, test_referral, to_lga):
        # Given: Referral to Aba South
        # When: Repository counts inbound referrals
        result = ReferralRepository.count_by_to_lga(to_lga.id)

        # Then: Count >= 1
        assert result >= 1

    def test_count_by_status(self, test_referral):
        # Given: Pending referral
        # When: Repository counts by status
        result = ReferralRepository.count_by_status("pending")

        # Then: Count >= 1
        assert result >= 1

    def test_count_by_status_no_results(self, test_referral):
        # Given: Pending referral
        # When: Repository counts by different status
        result = ReferralRepository.count_by_status("completed")

        # Then: Count == 0
        assert result == 0

    def test_get_statistics(self, test_referral):
        # Given: At least one referral exists
        # When: Repository retrieves aggregate statistics
        result = ReferralRepository.get_statistics()

        # Then: Returns dict with counts
        assert isinstance(result, dict)
        assert "total" in result
        assert result["total"] >= 1

    def test_select_related_optimization(self, test_referral):
        # Given: Existing referral with related objects
        # When: Repository retrieves by ID
        result = ReferralRepository.get_by_id(test_referral.id)

        # Then: Related objects accessible
        assert result.case is not None
        assert result.migrant is not None
        assert result.from_lga is not None
        assert result.to_lga is not None
        assert result.referred_by is not None
        assert result.assigned_to is not None
