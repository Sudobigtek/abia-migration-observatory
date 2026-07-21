
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.cases.repositories import CaseRepository


@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_user(test_lga):
    return User.objects.create_user(
        username="caseuser",
        password="CasePass123!",
        role="field_officer",
        lga=test_lga,
    )


@pytest.fixture
def test_migrant(test_lga):
    return Migrant.objects.create(
        full_name="Case Subject",
        phone="+2348033333333",
        date_of_birth=date(1992, 3, 3),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )


@pytest.fixture
def test_case(test_user, test_migrant, test_lga):
    return Case.objects.create(
        migrant=test_migrant,
        lga=test_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="medium",
        case_type="protection",
        description="Test case",
    )


@pytest.mark.django_db
class TestCaseRepository:
    def test_get_all_cases(self, test_case):
        result = CaseRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_case):
        result = CaseRepository.get_by_id(test_case.id)
        assert result is not None
        assert result.description == "Test case"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = CaseRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_case, test_lga):
        result = CaseRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_case.id).exists()

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
            "description": "New case",
        }
        result = CaseRepository.create(data)
        assert result.id is not None
        assert result.priority == "high"

    def test_update_case(self, test_case):
        updated = CaseRepository.update(test_case.id, {"status": "in_progress"})
        assert updated.status == "in_progress"
