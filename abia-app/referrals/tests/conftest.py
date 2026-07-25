import pytest
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case

@pytest.fixture
def from_lga():
    return LGA.objects.get(name="Aba North")

@pytest.fixture
def to_lga():
    return LGA.objects.get(name="Aba South")

@pytest.fixture
def test_user(from_lga):
    return User.objects.create_user(
        username="refuser",
        password="RefPass123!",
        role="field_officer",
        lga=from_lga,
    )

@pytest.fixture
def test_migrant(from_lga):
    return Migrant.objects.create(
        full_name="Referral Subject",
        phone="+2348044444444",
        date_of_birth=date(1988, 8, 8),
        gender="female",
        current_lga=from_lga,
        lga_of_origin=from_lga,
        status="active",
    )

@pytest.fixture
def test_case(test_user, test_migrant, from_lga):
    return Case.objects.create(
        migrant=test_migrant,
        lga=from_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="high",
        case_type="medical",
        description="Case for referral",
    )
