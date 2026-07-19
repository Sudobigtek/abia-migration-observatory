import pytest
from uuid import uuid4
from abia.migrants.models import Migrant
from abia.migrants.repositories import MigrantRepository
from abia.accounts.models import LGA


@pytest.mark.django_db
class TestMigrantRepository:
    def test_get_all(self, test_user):
        assert MigrantRepository.get_all().count() == 0

    def test_get_by_id(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
            current_lga=lga,
            created_by=test_user,
        )
        result = MigrantRepository.get_by_id(migrant.id)
        assert result == migrant

    def test_get_by_id_not_found(self):
        result = MigrantRepository.get_by_id(uuid4())
        assert result is None

    def test_get_by_lga(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
            current_lga=lga,
            created_by=test_user,
        )
        results = MigrantRepository.get_by_lga(lga.id)
        assert migrant in list(results)

    def test_create(self, test_user):
        lga = LGA.objects.first()
        migrant = MigrantRepository.create({
            "full_name": "Jane Doe",
            "phone": "+2348098765432",
            "current_lga": lga,
            "created_by": test_user,
        })
        assert migrant.full_name == "Jane Doe"
        assert migrant.phone == "+2348098765432"

    def test_update(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
            current_lga=lga,
            created_by=test_user,
        )
        updated = MigrantRepository.update(migrant.id, {"full_name": "John Updated"})
        assert updated.full_name == "John Updated"
