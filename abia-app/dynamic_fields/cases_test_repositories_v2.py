"""Integration tests for abia.cases.repositories module.

Uses real PostgreSQL database. Tests match actual repository methods:
- CaseRepository: create, get_all, get_by_id, get_by_lga, get_by_migrant, update

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from abia.accounts.models import LGA, User
from abia.cases.models import Case
from abia.cases.repositories import CaseRepository
from abia.migrants.models import Migrant


@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_lga_2():
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_user(test_lga):
    user = User.objects.create_user(
        username="caseofficer",
        password="CasePass123!",
        role="field_officer",
        lga=test_lga,
    )
    return user


@pytest.fixture
def test_migrant(test_lga):
    from datetime import date

    migrant = Migrant.objects.create(
        full_name="Case Subject",
        phone="+2348011111111",
        date_of_birth=date(1995, 1, 1),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )
    return migrant


@pytest.fixture
def test_case(test_user, test_migrant, test_lga):
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
    def test_get_all_cases(self, test_case):
        result = CaseRepository.get_all()
        assert result.count() >= 1
        assert result.filter(id=test_case.id).exists()

    def test_get_by_id_existing(self, test_case):
        result = CaseRepository.get_by_id(test_case.id)
        assert result is not None
        assert result.description == "Test case for repository integration"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = CaseRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_case, test_lga):
        result = CaseRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_case.id).exists()

    def test_get_by_lga_empty(self, test_lga_2):
        result = CaseRepository.get_by_lga(test_lga_2.id)
        assert result.count() == 0

    def test_get_by_migrant(self, test_case, test_migrant):
        result = CaseRepository.get_by_migrant(test_migrant.id)
        assert result.filter(id=test_case.id).exists()

    def test_create_case(self, test_user, test_migrant, test_lga):
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
        result = CaseRepository.create(data)
        assert result.id is not None
        assert result.priority == "high"
        assert result.case_type == "medical"
        assert result.created_by_id == test_user.id

    def test_update_case_status(self, test_case):
        updated = CaseRepository.update(test_case.id, {"status": "in_progress"})
        assert updated.status == "in_progress"

    def test_update_case_priority(self, test_case):
        updated = CaseRepository.update(test_case.id, {"priority": "urgent"})
        assert updated.priority == "urgent"

    def test_update_case_assigned_to(self, test_case, test_lga):
        new_user = User.objects.create_user(
            username="newassignee",
            password="NewPass123!",
            role="field_officer",
            lga=test_lga,
        )
        updated = CaseRepository.update(test_case.id, {"assigned_to": new_user})
        assert updated.assigned_to_id == new_user.id

    def test_update_nonexistent_case(self):
        fake_id = uuid4()
        result = CaseRepository.update(fake_id, {"status": "closed"})
        assert result is None
