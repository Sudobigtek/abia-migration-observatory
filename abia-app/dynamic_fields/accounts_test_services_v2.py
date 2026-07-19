"""Unit tests for abia.accounts.services module.

Tests use mocked repositories (abia.accounts.repositories).
Matches actual repository methods: get_all, get_by_id, get_by_code, create, create_superuser, get_by_lga, get_by_username, update

Per Architecture Contract §8.1: Unit tests = 80% of pyramid.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from abia.accounts.repositories import LGARepository, UserRepository
from abia.accounts.services import LGAService, UserService
from common.exceptions import (
    InvalidRoleError,
    LGAAccessDenied,
    LGANotFoundError,
    UserNotFoundError,
)

# ───────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────


@pytest.fixture
def mock_lga():
    lga = MagicMock()
    lga.id = uuid4()
    lga.name = "Aba North"
    lga.code = "ABN"
    lga.population_2023 = 250000
    lga.boundary = None
    return lga


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.username = "testuser"
    user.role = "field_officer"
    user.lga_id = uuid4()
    user.lga = MagicMock()
    user.lga.name = "Aba North"
    user.phone = "+2348012345678"
    user.is_active = True
    return user


@pytest.fixture
def state_admin_user(mock_user):
    mock_user.role = "state_admin"
    return mock_user


@pytest.fixture
def super_admin_user(mock_user):
    mock_user.role = "super_admin"
    return mock_user


# ───────────────────────────────────────────────────────────────
# LGAService Tests
# ───────────────────────────────────────────────────────────────


class TestLGAService:
    """Test suite for LGAService."""

    def test_get_all_lgas(self, mock_lga):
        with patch.object(
            LGARepository, "get_all", return_value=[mock_lga]
        ) as mock_repo:
            result = LGAService.get_all_lgas()
            mock_repo.assert_called_once()
            assert len(result) == 1
            assert result[0].name == "Aba North"

    def test_get_lga_by_id_found(self, mock_lga):
        with patch.object(
            LGARepository, "get_by_id", return_value=mock_lga
        ) as mock_repo:
            result = LGAService.get_lga_by_id(mock_lga.id)
            mock_repo.assert_called_once_with(mock_lga.id)
            assert result.name == "Aba North"

    def test_get_lga_by_id_not_found(self):
        lga_id = uuid4()
        with patch.object(LGARepository, "get_by_id", return_value=None) as mock_repo:
            with pytest.raises(LGANotFoundError) as exc_info:
                LGAService.get_lga_by_id(lga_id)
            mock_repo.assert_called_once_with(lga_id)
            assert str(lga_id) in str(exc_info.value)

    def test_get_lga_by_code_found(self, mock_lga):
        with patch.object(
            LGARepository, "get_by_code", return_value=mock_lga
        ) as mock_repo:
            result = LGAService.get_lga_by_code("ABN")
            mock_repo.assert_called_once_with("ABN")
            assert result.code == "ABN"

    def test_get_lga_by_code_not_found(self):
        with patch.object(LGARepository, "get_by_code", return_value=None) as mock_repo:
            with pytest.raises(LGANotFoundError) as exc_info:
                LGAService.get_lga_by_code("XXX")
            mock_repo.assert_called_once_with("XXX")
            assert "XXX" in str(exc_info.value)

    def test_validate_lga_exists(self, mock_lga):
        with patch.object(LGARepository, "get_by_id", return_value=mock_lga):
            result = LGAService.validate_lga(mock_lga.id)
            assert result is True

    def test_validate_lga_not_exists(self):
        lga_id = uuid4()
        with patch.object(LGARepository, "get_by_id", return_value=None):
            with pytest.raises(LGANotFoundError):
                LGAService.validate_lga(lga_id)


# ───────────────────────────────────────────────────────────────
# UserService Tests — RLS Enforcement
# ───────────────────────────────────────────────────────────────


class TestUserServiceRLS:
    """Test suite for UserService Row-Level Security."""

    def test_get_users_for_request_field_officer(self, mock_user):
        with patch.object(
            UserRepository, "get_by_lga", return_value=[mock_user]
        ) as mock_repo:
            result = UserService.get_users_for_request(mock_user)
            mock_repo.assert_called_once_with(mock_user.lga_id)
            assert len(result) == 1

    def test_get_users_for_request_state_admin(self, state_admin_user):
        with patch.object(
            UserRepository, "get_all", return_value=[state_admin_user]
        ) as mock_repo:
            result = UserService.get_users_for_request(state_admin_user)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_users_for_request_super_admin(self, super_admin_user):
        with patch.object(
            UserRepository, "get_all", return_value=[super_admin_user]
        ) as mock_repo:
            result = UserService.get_users_for_request(super_admin_user)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_create_user_field_officer_same_lga(self, mock_user, mock_lga):
        mock_user.lga_id = mock_lga.id
        data = {"username": "newofficer", "lga": mock_lga.id}
        with patch.object(
            UserRepository, "create", return_value=MagicMock()
        ) as mock_repo:
            result = UserService.create_user(data, mock_user)
            mock_repo.assert_called_once()
            assert result is not None

    def test_create_user_field_officer_different_lga(self, mock_user):
        other_lga_id = uuid4()
        data = {"username": "newofficer", "lga": other_lga_id}
        with pytest.raises(LGAAccessDenied) as exc_info:
            UserService.create_user(data, mock_user)
        assert "outside your LGA" in str(exc_info.value)

    def test_create_user_state_admin_any_lga(self, state_admin_user):
        any_lga_id = uuid4()
        data = {"username": "newofficer", "lga": any_lga_id}
        with patch.object(
            UserRepository, "create", return_value=MagicMock()
        ) as mock_repo:
            result = UserService.create_user(data, state_admin_user)
            mock_repo.assert_called_once()
            assert result is not None

    def test_get_user_by_id_found_same_lga(self, mock_user):
        target_user = MagicMock()
        target_user.lga_id = mock_user.lga_id
        target_user.id = uuid4()
        with patch.object(
            UserRepository, "get_by_id", return_value=target_user
        ) as mock_repo:
            result = UserService.get_user_by_id(target_user.id, mock_user)
            mock_repo.assert_called_once_with(target_user.id)
            assert result == target_user

    def test_get_user_by_id_field_officer_other_lga(self, mock_user):
        target_user = MagicMock()
        target_user.lga_id = uuid4()
        target_user.id = uuid4()
        with patch.object(UserRepository, "get_by_id", return_value=target_user):
            with pytest.raises(LGAAccessDenied):
                UserService.get_user_by_id(target_user.id, mock_user)

    def test_get_user_by_id_not_found(self, mock_user):
        user_id = uuid4()
        with patch.object(UserRepository, "get_by_id", return_value=None) as mock_repo:
            with pytest.raises(UserNotFoundError):
                UserService.get_user_by_id(user_id, mock_user)
            mock_repo.assert_called_once_with(user_id)

    def test_update_user_field_officer_same_lga(self, mock_user):
        update_data = {"first_name": "Updated"}
        updated_user = MagicMock()
        updated_user.first_name = "Updated"
        updated_user.lga_id = mock_user.lga_id
        with patch.object(
            UserRepository, "get_by_id", return_value=mock_user
        ), patch.object(
            UserRepository, "update", return_value=updated_user
        ) as mock_update:
            result = UserService.update_user(mock_user.id, update_data, mock_user)
            mock_update.assert_called_once()
            assert result.first_name == "Updated"

    def test_update_user_field_officer_other_lga(self, mock_user):
        other_user = MagicMock()
        other_user.id = uuid4()
        other_user.lga_id = uuid4()
        update_data = {"first_name": "Updated"}
        with patch.object(UserRepository, "get_by_id", return_value=other_user):
            with pytest.raises(LGAAccessDenied):
                UserService.update_user(other_user.id, update_data, mock_user)

    def test_validate_role_valid(self):
        assert UserService.validate_role("field_officer") is True
        assert UserService.validate_role("lga_coordinator") is True
        assert UserService.validate_role("state_admin") is True
        assert UserService.validate_role("super_admin") is True

    def test_validate_role_invalid(self):
        with pytest.raises(InvalidRoleError):
            UserService.validate_role("invalid_role")
        with pytest.raises(InvalidRoleError):
            UserService.validate_role("")

    def test_can_access_lga_field_officer_same(self, mock_user):
        assert UserService.can_access_lga(mock_user, mock_user.lga_id) is True

    def test_can_access_lga_field_officer_different(self, mock_user):
        other_lga_id = uuid4()
        assert UserService.can_access_lga(mock_user, other_lga_id) is False

    def test_can_access_lga_state_admin(self, state_admin_user):
        any_lga_id = uuid4()
        assert UserService.can_access_lga(state_admin_user, any_lga_id) is True
