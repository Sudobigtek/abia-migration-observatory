"""Integration tests for abia.referrals.repositories module.

Uses real PostgreSQL database. Tests match actual repository methods:
- ReferralRepository: create, get_all, get_by_case, get_by_id, get_by_lga, update

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from abia.accounts.models import LGA, User
from abia.cases.models import Case
from abia.migrants.models import Migrant
from abia.referrals.models import Referral
from abia.referrals.repositories import ReferralRepository


@pytest.fixture
def from_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def to_lga():
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_user(from_lga):
    user = User.objects.create_user(
        username="referralofficer",
        password="RefPass123!",
        role="field_officer",
        lga=from_lga,
    )
    return user


@pytest.fixture
def test_migrant(from_lga):
    from datetime import date

    migrant = Migrant.objects.create(
        full_name="Referral Subject",
        phone="+2348022222222",
        date_of_birth=date(1992, 6, 10),
        gender="female",
        current_lga=from_lga,
        lga_of_origin=from_lga,
        status="active",
    )
    return migrant


@pytest.fixture
def test_case(test_user, test_migrant, from_lga):
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
def test_referral(test_case, from_lga, to_lga, test_user):
    referral = Referral.objects.create(
        case=test_case,
        from_lga=from_lga,
        to_lga=to_lga,
        to_organization="Specialist Hospital",
        to_contact_name="Dr. Smith",
        to_contact_phone="+2348099999999",
        reason="Medical emergency requiring specialist care",
        status="pending",
        created_by=test_user,
    )
    return referral


@pytest.mark.django_db
class TestReferralRepository:
    def test_get_all_referrals(self, test_referral):
        result = ReferralRepository.get_all()
        assert result.count() >= 1
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_id_existing(self, test_referral):
        result = ReferralRepository.get_by_id(test_referral.id)
        assert result is not None
        assert result.reason == "Medical emergency requiring specialist care"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = ReferralRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_referral, from_lga):
        result = ReferralRepository.get_by_lga(from_lga.id)
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_lga_empty(self, to_lga):
        result = ReferralRepository.get_by_lga(to_lga.id)
        assert result.count() == 0

    def test_get_by_case(self, test_referral, test_case):
        result = ReferralRepository.get_by_case(test_case.id)
        assert result.filter(id=test_referral.id).exists()

    def test_create_referral(self, test_case, from_lga, to_lga, test_user):
        data = {
            "case": test_case,
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "General Hospital",
            "to_contact_name": "Dr. Jones",
            "to_contact_phone": "+2348088888888",
            "reason": "Follow-up care needed",
            "status": "pending",
            "created_by": test_user,
        }
        result = ReferralRepository.create(data)
        assert result.id is not None
        assert result.status == "pending"
        assert result.from_lga_id == from_lga.id
        assert result.to_lga_id == to_lga.id
        assert result.to_organization == "General Hospital"

    def test_update_referral_status(self, test_referral):
        updated = ReferralRepository.update(test_referral.id, {"status": "in_progress"})
        assert updated.status == "in_progress"

    def test_update_referral_to_organization(self, test_referral):
        updated = ReferralRepository.update(
            test_referral.id, {"to_organization": "Updated Hospital"}
        )
        assert updated.to_organization == "Updated Hospital"

    def test_update_referral_to_contact(self, test_referral):
        updated = ReferralRepository.update(
            test_referral.id,
            {"to_contact_name": "Dr. Updated", "to_contact_phone": "+2348077777777"},
        )
        assert updated.to_contact_name == "Dr. Updated"
        assert updated.to_contact_phone == "+2348077777777"

    def test_update_nonexistent_referral(self):
        fake_id = uuid4()
        result = ReferralRepository.update(fake_id, {"status": "in_progress"})
        assert result is None
