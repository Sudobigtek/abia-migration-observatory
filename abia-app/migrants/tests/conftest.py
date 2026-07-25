import pytest
from abia.accounts.models import LGA

@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")
