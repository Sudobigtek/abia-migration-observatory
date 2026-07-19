"""Integration tests for abia.migrants.repositories module.

Uses real PostgreSQL database. Tests match actual repository methods:
- MigrantRepository: create, get_all, get_by_id, get_by_lga, update

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import date
from uuid import uuid4

import pytest

from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.migrants.repositories import MigrantRepository


@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_lga_2():
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_migrant(test_lga):
    migrant = Migrant.objects.create(
        full_name="John Doe",
        phone="+2348012345678",
        date_of_birth=date(1990, 5, 15),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )
    return migrant


@pytest.mark.django_db
class TestMigrantRepository:
    def test_get_all_migrants(self, test_migrant):
        result = MigrantRepository.get_all()
        assert result.count() >= 1
        assert result.filter(id=test_migrant.id).exists()

    def test_get_by_id_existing(self, test_migrant):
        result = MigrantRepository.get_by_id(test_migrant.id)
        assert result is not None
        assert result.full_name == "John Doe"
        assert result.phone == "+2348012345678"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = MigrantRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_migrant, test_lga):
        result = MigrantRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_migrant.id).exists()

    def test_get_by_lga_empty(self, test_lga_2):
        result = MigrantRepository.get_by_lga(test_lga_2.id)
        assert result.count() == 0

    def test_create_migrant(self, test_lga):
        data = {
            "full_name": "Jane Smith",
            "phone": "+2348098765432",
            "date_of_birth": date(1985, 3, 20),
            "gender": "female",
            "current_lga": test_lga,
            "lga_of_origin": test_lga,
            "status": "active",
        }
        result = MigrantRepository.create(data)
        assert result.id is not None
        assert result.full_name == "Jane Smith"
        assert result.phone == "+2348098765432"
        assert result.current_lga_id == test_lga.id

    def test_update_migrant_full_name(self, test_migrant):
        updated = MigrantRepository.update(
            test_migrant.id, {"full_name": "Updated Name"}
        )
        assert updated.full_name == "Updated Name"

    def test_update_migrant_status(self, test_migrant):
        updated = MigrantRepository.update(test_migrant.id, {"status": "inactive"})
        assert updated.status == "inactive"
        test_migrant.status = "active"
        test_migrant.save()

    def test_update_migrant_lga(self, test_migrant, test_lga_2):
        updated = MigrantRepository.update(test_migrant.id, {"current_lga": test_lga_2})
        assert updated.current_lga_id == test_lga_2.id
        test_migrant.current_lga = test_lga
        test_migrant.save()

    def test_update_nonexistent_migrant(self):
        fake_id = uuid4()
        result = MigrantRepository.update(fake_id, {"full_name": "Ghost"})
        assert result is None
