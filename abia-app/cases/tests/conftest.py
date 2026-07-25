import pytest
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant

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
