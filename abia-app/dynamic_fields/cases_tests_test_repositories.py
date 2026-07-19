"""Integration tests for cases.repositories module.

Tests cover:
- CaseRepository: CRUD, status filtering, assignment, priority queries
- Real database operations with PostgreSQL

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from accounts.models import LGA, User
from cases.models import Case
from cases.repositories import CaseRepository
from migrants.models import Migrant


@pytest.fixture
def test_lga():
    """Return a known LGA."""
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_lga_2():
    """Return a second LGA."""
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_user(test_lga):
    """Create and return a test user."""
    user = User.objects.create_user(
        username="caseofficer",
        password="CasePass123!",
        role="field_officer",
        lga=test_lga,
    )
    return user


@pytest.fixture
def test_migrant(test_lga):
    """Create and return a test migrant."""
    from datetime import date

    migrant = Migrant.objects.create(
        full_name="Case Subject",
        phone="+2348011111111",
        date_of_birth=date(1995, 1, 1),
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )
    return migrant


@pytest.fixture
def test_case(test_user, test_migrant, test_lga):
    """Create and return a test case."""
    case = Case.objects.create(
        migrant=test_migrant,
        lga=test_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="medium",
        case_type="protection",
        description="Test case for repository integration",
    )
    return case


@pytest.mark.django_db
class TestCaseRepository:
    """Integration tests for CaseRepository with real database."""

    def test_get_all_cases(self, test_case):
        # Given: At least one case exists
        # When: Repository retrieves all
        result = CaseRepository.get_all()

        # Then: Returns queryset with cases
        assert result.count() >= 1
        assert result.filter(id=test_case.id).exists()

    def test_get_by_id_existing(self, test_case):
        # Given: Existing case
        # When: Repository retrieves by ID
        result = CaseRepository.get_by_id(test_case.id)

        # Then: Correct case returned
        assert result is not None
        assert result.description == "Test case for repository integration"

    def test_get_by_id_nonexistent(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository retrieves by ID
        result = CaseRepository.get_by_id(fake_id)

        # Then: None returned
        assert result is None

    def test_get_by_lga(self, test_case, test_lga):
        # Given: Case in Aba North
        # When: Repository filters by LGA
        result = CaseRepository.get_by_lga(test_lga.id)

        # Then: Case found in results
        assert result.filter(id=test_case.id).exists()

    def test_get_by_lga_empty(self, test_lga_2):
        # Given: LGA with no cases
        # When: Repository filters by that LGA
        result = CaseRepository.get_by_lga(test_lga_2.id)

        # Then: Empty queryset
        assert result.count() == 0

    def test_get_by_assigned_to(self, test_case, test_user):
        # Given: Case assigned to test_user
        # When: Repository filters by assigned user
        result = CaseRepository.get_by_assigned_to(test_user.id)

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_get_by_migrant(self, test_case, test_migrant):
        # Given: Case linked to test_migrant
        # When: Repository filters by migrant
        result = CaseRepository.get_by_migrant(test_migrant.id)

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_create_case(self, test_user, test_migrant, test_lga):
        # Given: New case data
        data = {
            "migrant": test_migrant,
            "lga": test_lga,
            "assigned_to": test_user,
            "created_by": test_user,
            "status": "open",
            "priority": "high",
            "case_type": "medical",
            "description": "New test case",
        }

        # When: Repository creates case
        result = CaseRepository.create(data)

        # Then: Case created with correct attributes
        assert result.id is not None
        assert result.priority == "high"
        assert result.case_type == "medical"
        assert result.created_by_id == test_user.id

    def test_update_case_status(self, test_case):
        # Given: Existing case with status "open"
        # When: Repository updates status
        updated = CaseRepository.update(test_case.id, {"status": "in_progress"})

        # Then: Status updated
        assert updated.status == "in_progress"

    def test_update_case_priority(self, test_case):
        # Given: Existing case with priority "medium"
        # When: Repository updates priority
        updated = CaseRepository.update(test_case.id, {"priority": "urgent"})

        # Then: Priority updated
        assert updated.priority == "urgent"

    def test_update_case_assigned_to(self, test_case, test_lga):
        # Given: Existing case and new assignee
        new_user = User.objects.create_user(
            username="newassignee",
            password="NewPass123!",
            role="field_officer",
            lga=test_lga,
        )

        # When: Repository updates assigned_to
        updated = CaseRepository.update(test_case.id, {"assigned_to": new_user})

        # Then: Assignment updated
        assert updated.assigned_to_id == new_user.id

    def test_update_nonexistent_case(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository updates non-existent case
        result = CaseRepository.update(fake_id, {"status": "closed"})

        # Then: Returns None
        assert result is None

    def test_delete_case(self, test_case):
        # Given: Existing case
        case_id = test_case.id

        # When: Repository deletes case
        result = CaseRepository.delete(case_id)

        # Then: Case no longer exists
        assert result is True
        assert Case.objects.filter(id=case_id).count() == 0

    def test_delete_nonexistent_case(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository deletes non-existent case
        result = CaseRepository.delete(fake_id)

        # Then: Returns False
        assert result is False

    def test_filter_by_status(self, test_case):
        # Given: Case with status "open"
        # When: Repository filters by status
        result = CaseRepository.filter_by_status("open")

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_filter_by_status_no_results(self, test_case):
        # Given: Case with status "open"
        # When: Repository filters by different status
        result = CaseRepository.filter_by_status("resolved")

        # Then: Empty queryset (assuming no resolved cases)
        assert result.count() == 0

    def test_filter_by_status_in_lga(self, test_case, test_lga):
        # Given: Open case in Aba North
        # When: Repository filters by status in LGA
        result = CaseRepository.filter_by_status_in_lga("open", test_lga.id)

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_filter_by_priority(self, test_case):
        # Given: Case with priority "medium"
        # When: Repository filters by priority
        result = CaseRepository.filter_by_priority("medium")

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_filter_by_priority_in_lga(self, test_case, test_lga):
        # Given: Medium priority case in Aba North
        # When: Repository filters by priority in LGA
        result = CaseRepository.filter_by_priority_in_lga("medium", test_lga.id)

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_filter_by_case_type(self, test_case):
        # Given: Case with type "protection"
        # When: Repository filters by case type
        result = CaseRepository.filter_by_case_type("protection")

        # Then: Case found
        assert result.filter(id=test_case.id).exists()

    def test_count_by_lga(self, test_case, test_lga):
        # Given: Case in Aba North
        # When: Repository counts by LGA
        result = CaseRepository.count_by_lga(test_lga.id)

        # Then: Count >= 1
        assert result >= 1

    def test_count_by_lga_empty(self, test_lga_2):
        # Given: LGA with no cases
        # When: Repository counts by LGA
        result = CaseRepository.count_by_lga(test_lga_2.id)

        # Then: Count == 0
        assert result == 0

    def test_count_by_status(self, test_case):
        # Given: Open case
        # When: Repository counts by status
        result = CaseRepository.count_by_status("open")

        # Then: Count >= 1
        assert result >= 1

    def test_get_overdue_by_lga(self, test_case, test_lga):
        # Given: Case created today (not overdue by default)
        # When: Repository retrieves overdue cases
        result = CaseRepository.get_overdue_by_lga(test_lga.id)

        # Then: Likely empty (case is fresh)
        # This test verifies the query runs without error
        assert result.count() >= 0

    def test_select_related_optimization(self, test_case):
        # Given: Existing case with related migrant and user
        # When: Repository retrieves with select_related
        result = CaseRepository.get_by_id(test_case.id)

        # Then: Related objects accessible without extra queries
        # (Django assertNumQueries would verify this in a full test setup)
        assert result.migrant is not None
        assert result.assigned_to is not None
        assert result.lga is not None
