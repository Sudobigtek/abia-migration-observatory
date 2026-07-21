
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.migrants.repositories import MigrantRepository


@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_migrant(test_lga):
    return Migrant.objects.create(
        full_name="Test Migrant",
        phone="+2348011111111",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )


@pytest.mark.django_db
class TestMigrantRepository:
    def test_get_all_migrants(self, test_migrant):
        result = MigrantRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_migrant):
        result = MigrantRepository.get_by_id(test_migrant.id)
        assert result is not None
        assert result.full_name == "Test Migrant"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = MigrantRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_migrant, test_lga):
        result = MigrantRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_migrant.id).exists()

    def test_create_migrant(self, test_lga):
        data = {
            "full_name": "New Migrant",
            "phone": "+2348022222222",
            "date_of_birth": date(1985, 5, 15),
            "gender": "female",
            "current_lga": test_lga,
            "lga_of_origin": test_lga,
            "status": "active",
        }
        result = MigrantRepository.create(data)
        assert result.id is not None
        assert result.full_name == "New Migrant"

    def test_update_migrant(self, test_migrant):
        updated = MigrantRepository.update(test_migrant.id, {"full_name": "Updated Name"})
        assert updated.full_name == "Updated Name"
