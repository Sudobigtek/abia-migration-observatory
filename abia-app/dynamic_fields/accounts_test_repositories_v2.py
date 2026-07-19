"""Integration tests for abia.accounts.repositories module.

Uses real PostgreSQL database. Tests match actual repository methods:
- LGARepository: get_all, get_by_code, get_by_id
- UserRepository: create, create_superuser, get_all, get_by_id, get_by_lga, get_by_username

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from uuid import uuid4

import pytest

from abia.accounts.models import LGA, User
from abia.accounts.repositories import LGARepository, UserRepository


@pytest.mark.django_db
class TestLGARepository:
    """Integration tests for LGARepository with real database."""

    def test_get_all_returns_seeded_lgas(self):
        result = LGARepository.get_all()
        assert result.count() == 17

    def test_get_by_id_existing_lga(self):
        aba_north = LGA.objects.get(name="Aba North")
        result = LGARepository.get_by_id(aba_north.id)
        assert result is not None
        assert result.name == "Aba North"
        assert result.code == "ABN"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = LGARepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_code_existing(self):
        result = LGARepository.get_by_code("ABN")
        assert result is not None
        assert result.name == "Aba North"

    def test_get_by_code_nonexistent(self):
        result = LGARepository.get_by_code("XXX")
        assert result is None

    def test_get_by_code_case_sensitive(self):
        result_lower = LGARepository.get_by_code("abn")
        result_upper = LGARepository.get_by_code("ABN")
        assert result_lower is not None
        assert result_upper is not None
        assert result_lower.id == result_upper.id


@pytest.mark.django_db
class TestUserRepository:
    """Integration tests for UserRepository with real database."""

    @pytest.fixture
    def test_lga(self):
        return LGA.objects.get(name="Aba North")

    @pytest.fixture
    def test_user(self, test_lga):
        user = User.objects.create_user(
            username="testofficer",
            password="TestPass123!",
            role="field_officer",
            lga=test_lga,
        )
        return user

    def test_get_all_users(self, test_user):
        result = UserRepository.get_all()
        assert result.count() >= 2  # superuser + test_user

    def test_get_by_id_existing(self, test_user):
        result = UserRepository.get_by_id(test_user.id)
        assert result is not None
        assert result.username == "testofficer"
        assert result.role == "field_officer"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = UserRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_user, test_lga):
        result = UserRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_user.id).exists()

    def test_get_by_lga_empty(self, test_lga):
        empty_lga = LGA.objects.exclude(id=test_lga.id).first()
        result = UserRepository.get_by_lga(empty_lga.id)
        assert result.count() == 0

    def test_get_by_username(self, test_user):
        result = UserRepository.get_by_username("testofficer")
        assert result is not None
        assert result.id == test_user.id

    def test_get_by_username_nonexistent(self):
        result = UserRepository.get_by_username("nonexistent_user")
        assert result is None

    def test_create_user(self, test_lga):
        data = {
            "username": "newofficer",
            "password": "NewPass456!",
            "role": "field_officer",
            "lga": test_lga,
        }
        result = UserRepository.create(data)
        assert result.id is not None
        assert result.username == "newofficer"
        assert result.role == "field_officer"
        assert result.lga_id == test_lga.id
        assert result.check_password("NewPass456!")

    def test_create_superuser(self, test_lga):
        data = {
            "username": "superuser2",
            "password": "SuperPass123!",
            "role": "super_admin",
            "lga": test_lga,
        }
        result = UserRepository.create_superuser(data)
        assert result is not None
        assert result.is_superuser is True
        assert result.role == "super_admin"

    def test_create_user_duplicate_username(self, test_user):
        data = {
            "username": "testofficer",
            "password": "AnotherPass!",
            "role": "field_officer",
            "lga": test_user.lga,
        }
        with pytest.raises(Exception):
            UserRepository.create(data)

    def test_update_user_role(self, test_user):
        updated = UserRepository.update(test_user.id, {"role": "lga_coordinator"})
        assert updated.role == "lga_coordinator"
        test_user.role = "field_officer"
        test_user.save()

    def test_update_user_lga(self, test_user):
        new_lga = LGA.objects.exclude(id=test_user.lga_id).first()
        updated = UserRepository.update(test_user.id, {"lga": new_lga})
        assert updated.lga_id == new_lga.id
        test_user.lga = LGA.objects.get(id=test_user.lga_id)
        test_user.save()
