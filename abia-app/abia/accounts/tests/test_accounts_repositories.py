import pytest
from uuid import uuid4
from abia.accounts.models import LGA, User
from abia.accounts.repositories import LGARepository, UserRepository


@pytest.mark.django_db
class TestLGARepository:
    def test_get_all(self):
        lgas = LGARepository.get_all()
        assert lgas.count() == 17

    def test_get_by_id(self):
        lga = LGA.objects.first()
        result = LGARepository.get_by_id(lga.id)
        assert result == lga

    def test_get_by_id_not_found(self):
        result = LGARepository.get_by_id(uuid4())
        assert result is None

    def test_get_by_code(self):
        lga = LGA.objects.first()
        result = LGARepository.get_by_code(lga.code)
        assert result == lga

    def test_get_by_code_not_found(self):
        result = LGARepository.get_by_code("NONEXISTENT")
        assert result is None


@pytest.mark.django_db
class TestUserRepository:
    def test_get_all(self):
        users = UserRepository.get_all()
        assert users.count() >= 1

    def test_get_by_id(self, test_user):
        result = UserRepository.get_by_id(test_user.id)
        assert result == test_user

    def test_get_by_id_not_found(self):
        result = UserRepository.get_by_id(uuid4())
        assert result is None

    def test_get_by_lga(self, test_user):
        results = UserRepository.get_by_lga(test_user.lga.id)
        assert test_user in list(results)

    def test_get_by_username(self, test_user):
        result = UserRepository.get_by_username(test_user.username)
        assert result == test_user

    def test_get_by_username_not_found(self):
        result = UserRepository.get_by_username("nonexistent")
        assert result is None

    def test_create(self):
        lga = LGA.objects.first()
        user = UserRepository.create({
            "username": "newuser",
            "password": "NewPass123",
            "role": "field_officer",
            "lga": lga,
        })
        assert user.username == "newuser"
        assert user.role == "field_officer"

    def test_create_superuser(self):
        lga = LGA.objects.first()
        user = UserRepository.create_superuser({
            "username": "superuser",
            "password": "SuperPass123",
            "role": "super_admin",
            "lga": lga,
        })
        assert user.username == "superuser"
        assert user.is_superuser is True
