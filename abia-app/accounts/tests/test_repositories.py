
import pytest
from uuid import uuid4
from abia.accounts.models import LGA, User
from abia.accounts.repositories import LGARepository, UserRepository


@pytest.mark.django_db
class TestLGARepository:
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


@pytest.mark.django_db
class TestUserRepository:
    def test_get_all_users(self):
        result = UserRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self):
        user = User.objects.first()
        result = UserRepository.get_by_id(user.id)
        assert result is not None

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = UserRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self):
        lga = LGA.objects.first()
        result = UserRepository.get_by_lga(lga.id)
        assert result.count() >= 0

    def test_get_by_username_existing(self):
        user = User.objects.first()
        result = UserRepository.get_by_username(user.username)
        assert result is not None

    def test_get_by_username_nonexistent(self):
        result = UserRepository.get_by_username("nonexistent_xyz")
        assert result is None

    def test_create_user(self):
        lga = LGA.objects.first()
        data = {
            "username": "testuser_repo",
            "password": "TestPass123!",
            "role": "field_officer",
            "lga": lga,
        }
        result = UserRepository.create(data)
        assert result.id is not None
        assert result.username == "testuser_repo"

    def test_create_superuser(self):
        lga = LGA.objects.first()
        data = {
            "username": "superuser_repo",
            "password": "SuperPass123!",
            "role": "super_admin",
            "lga": lga,
        }
        result = UserRepository.create_superuser(data)
        assert result.id is not None
        assert result.is_superuser is True
