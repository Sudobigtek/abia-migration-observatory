"""Unit tests for accounts.services module.

Tests cover:
- LGAService: LGA retrieval, validation
- UserService: RLS enforcement, user creation, role-based access

All tests use mocked repositories to ensure pure unit testing
(no database dependency per Architecture Contract §8.1).
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from accounts.repositories import LGARepository, UserRepository
from accounts.services import LGAService, UserService
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
    """Return a mocked LGA object."""
    lga = MagicMock()
    lga.id = uuid4()
    lga.name = "Aba North"
    lga.code = "ABN"
    lga.population = 250000
    return lga


@pytest.fixture
def mock_user():
    """Return a mocked User object with configurable role."""
    user = MagicMock()
    user.id = uuid4()
    user.username = "testuser"
    user.role = "field_officer"
    user.lga_id = uuid4()
    user.lga = MagicMock()
    user.lga.name = "Aba North"
    user.is_active = True
    return user


@pytest.fixture
def state_admin_user(mock_user):
    """Return a mocked state admin user."""
    mock_user.role = "state_admin"
    return mock_user


@pytest.fixture
def super_admin_user(mock_user):
    """Return a mocked super admin user."""
    mock_user.role = "super_admin"
    return mock_user


@pytest.fixture
def lga_coordinator_user(mock_user):
    """Return a mocked LGA coordinator user."""
    mock_user.role = "lga_coordinator"
    return mock_user


# ───────────────────────────────────────────────────────────────
# LGAService Tests
# ───────────────────────────────────────────────────────────────


class TestLGAService:
    """Test suite for LGAService business logic."""

    def test_get_all_lgas(self, mock_lga):
        # Given: Repository returns list of LGAs
        with patch.object(
            LGARepository, "get_all", return_value=[mock_lga]
        ) as mock_repo:
            # When: Service requests all LGAs
            result = LGAService.get_all_lgas()

            # Then: Repository called once, result returned
            mock_repo.assert_called_once()
            assert len(result) == 1
            assert result[0].name == "Aba North"

    def test_get_lga_by_id_found(self, mock_lga):
        # Given: Repository finds LGA by ID
        with patch.object(
            LGARepository, "get_by_id", return_value=mock_lga
        ) as mock_repo:
            # When: Service requests specific LGA
            result = LGAService.get_lga_by_id(mock_lga.id)

            # Then: Correct LGA returned
            mock_repo.assert_called_once_with(mock_lga.id)
            assert result.name == "Aba North"

    def test_get_lga_by_id_not_found(self):
        # Given: Repository returns None for unknown ID
        lga_id = uuid4()
        with patch.object(LGARepository, "get_by_id", return_value=None) as mock_repo:
            # When/Then: Service raises LGANotFoundError
            with pytest.raises(LGANotFoundError) as exc_info:
                LGAService.get_lga_by_id(lga_id)

            mock_repo.assert_called_once_with(lga_id)
            assert str(lga_id) in str(exc_info.value)

    def test_get_lga_by_name_found(self, mock_lga):
        # Given: Repository finds LGA by name
        with patch.object(
            LGARepository, "get_by_name", return_value=mock_lga
        ) as mock_repo:
            # When: Service requests LGA by name
            result = LGAService.get_lga_by_name("Aba North")

            # Then: Correct LGA returned
            mock_repo.assert_called_once_with("Aba North")
            assert result.code == "ABN"

    def test_get_lga_by_name_not_found(self):
        # Given: Repository returns None for unknown name
        with patch.object(LGARepository, "get_by_name", return_value=None) as mock_repo:
            # When/Then: Service raises LGANotFoundError
            with pytest.raises(LGANotFoundError) as exc_info:
                LGAService.get_lga_by_name("Unknown LGA")

            mock_repo.assert_called_once_with("Unknown LGA")
            assert "Unknown LGA" in str(exc_info.value)

    def test_validate_lga_exists(self, mock_lga):
        # Given: LGA exists in repository
        with patch.object(LGARepository, "get_by_id", return_value=mock_lga):
            # When: Service validates LGA
            result = LGAService.validate_lga(mock_lga.id)

            # Then: Returns True, no exception
            assert result is True

    def test_validate_lga_not_exists(self):
        # Given: LGA does not exist
        lga_id = uuid4()
        with patch.object(LGARepository, "get_by_id", return_value=None):
            # When/Then: Service raises LGANotFoundError
            with pytest.raises(LGANotFoundError):
                LGAService.validate_lga(lga_id)


# ───────────────────────────────────────────────────────────────
# UserService Tests — RLS Enforcement
# ───────────────────────────────────────────────────────────────


class TestUserServiceRLS:
    """Test suite for UserService Row-Level Security enforcement."""

    def test_get_users_for_request_field_officer(self, mock_user):
        # Given: Field officer with assigned LGA
        with patch.object(
            UserRepository, "get_by_lga", return_value=[mock_user]
        ) as mock_repo:
            # When: Service retrieves users for field officer
            result = UserService.get_users_for_request(mock_user)

            # Then: Only own LGA users returned
            mock_repo.assert_called_once_with(mock_user.lga_id)
            assert len(result) == 1

    def test_get_users_for_request_lga_coordinator(self, lga_coordinator_user):
        # Given: LGA coordinator with assigned LGA
        with patch.object(
            UserRepository, "get_by_lga", return_value=[lga_coordinator_user]
        ) as mock_repo:
            # When: Service retrieves users for coordinator
            result = UserService.get_users_for_request(lga_coordinator_user)

            # Then: Only own LGA users returned (same as field officer)
            mock_repo.assert_called_once_with(lga_coordinator_user.lga_id)
            assert len(result) == 1

    def test_get_users_for_request_state_admin(self, state_admin_user):
        # Given: State admin
        with patch.object(
            UserRepository, "get_all", return_value=[state_admin_user]
        ) as mock_repo:
            # When: Service retrieves users for state admin
            result = UserService.get_users_for_request(state_admin_user)

            # Then: All users returned (state-wide access)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_users_for_request_super_admin(self, super_admin_user):
        # Given: Super admin
        with patch.object(
            UserRepository, "get_all", return_value=[super_admin_user]
        ) as mock_repo:
            # When: Service retrieves users for super admin
            result = UserService.get_users_for_request(super_admin_user)

            # Then: All users returned (full access)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_create_user_field_officer_same_lga(self, mock_user, mock_lga):
        # Given: Field officer creating user in same LGA
        mock_user.lga_id = mock_lga.id
        data = {"username": "newofficer", "lga": mock_lga.id}

        with patch.object(
            UserRepository, "create", return_value=MagicMock()
        ) as mock_repo:
            # When: Service creates user
            result = UserService.create_user(data, mock_user)

            # Then: User created successfully
            mock_repo.assert_called_once()
            assert result is not None

    def test_create_user_field_officer_different_lga(self, mock_user):
        # Given: Field officer attempting to create user in different LGA
        other_lga_id = uuid4()
        data = {"username": "newofficer", "lga": other_lga_id}

        # When/Then: Access denied exception raised
        with pytest.raises(LGAAccessDenied) as exc_info:
            UserService.create_user(data, mock_user)

        assert "Cannot create user outside your LGA" in str(exc_info.value)

    def test_create_user_state_admin_any_lga(self, state_admin_user):
        # Given: State admin creating user in any LGA
        any_lga_id = uuid4()
        data = {"username": "newofficer", "lga": any_lga_id}

        with patch.object(
            UserRepository, "create", return_value=MagicMock()
        ) as mock_repo:
            # When: Service creates user
            result = UserService.create_user(data, state_admin_user)

            # Then: User created (state admin has cross-LGA access)
            mock_repo.assert_called_once()
            assert result is not None

    def test_create_user_super_admin_any_lga(self, super_admin_user):
        # Given: Super admin creating user in any LGA
        any_lga_id = uuid4()
        data = {"username": "newofficer", "lga": any_lga_id}

        with patch.object(
            UserRepository, "create", return_value=MagicMock()
        ) as mock_repo:
            # When: Service creates user
            result = UserService.create_user(data, super_admin_user)

            # Then: User created (super admin has full access)
            mock_repo.assert_called_once()
            assert result is not None

    def test_get_user_by_id_field_officer_own_lga(self, mock_user):
        # Given: Field officer requesting user in own LGA
        target_user = MagicMock()
        target_user.lga_id = mock_user.lga_id
        target_user.id = uuid4()

        with patch.object(
            UserRepository, "get_by_id", return_value=target_user
        ) as mock_repo:
            # When: Service retrieves user
            result = UserService.get_user_by_id(target_user.id, mock_user)

            # Then: User returned
            mock_repo.assert_called_once_with(target_user.id)
            assert result == target_user

    def test_get_user_by_id_field_officer_other_lga(self, mock_user):
        # Given: Field officer requesting user in different LGA
        target_user = MagicMock()
        target_user.lga_id = uuid4()  # Different from mock_user.lga_id
        target_user.id = uuid4()

        with patch.object(UserRepository, "get_by_id", return_value=target_user):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                UserService.get_user_by_id(target_user.id, mock_user)

    def test_get_user_by_id_not_found(self, mock_user):
        # Given: User ID does not exist
        user_id = uuid4()
        with patch.object(UserRepository, "get_by_id", return_value=None) as mock_repo:
            # When/Then: UserNotFoundError raised
            with pytest.raises(UserNotFoundError):
                UserService.get_user_by_id(user_id, mock_user)

            mock_repo.assert_called_once_with(user_id)

    def test_update_user_field_officer_same_lga(self, mock_user):
        # Given: Field officer updating user in same LGA
        target_user = MagicMock()
        target_user.lga_id = mock_user.lga_id
        target_user.id = uuid4()
        data = {"first_name": "Updated"}

        with patch.object(
            UserRepository, "get_by_id", return_value=target_user
        ), patch.object(
            UserRepository, "update", return_value=target_user
        ) as mock_update:
            # When: Service updates user
            result = UserService.update_user(target_user.id, data, mock_user)

            # Then: Update succeeds
            mock_update.assert_called_once()
            assert result == target_user

    def test_update_user_field_officer_other_lga(self, mock_user):
        # Given: Field officer updating user in different LGA
        target_user = MagicMock()
        target_user.lga_id = uuid4()
        target_user.id = uuid4()
        data = {"first_name": "Updated"}

        with patch.object(UserRepository, "get_by_id", return_value=target_user):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                UserService.update_user(target_user.id, data, mock_user)

    def test_delete_user_field_officer_same_lga(self, mock_user):
        # Given: Field officer deleting user in same LGA
        target_user = MagicMock()
        target_user.lga_id = mock_user.lga_id
        target_user.id = uuid4()

        with patch.object(
            UserRepository, "get_by_id", return_value=target_user
        ), patch.object(UserRepository, "delete", return_value=True) as mock_delete:
            # When: Service deletes user
            result = UserService.delete_user(target_user.id, mock_user)

            # Then: Delete succeeds
            mock_delete.assert_called_once()
            assert result is True

    def test_delete_user_field_officer_other_lga(self, mock_user):
        # Given: Field officer deleting user in different LGA
        target_user = MagicMock()
        target_user.lga_id = uuid4()
        target_user.id = uuid4()

        with patch.object(UserRepository, "get_by_id", return_value=target_user):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                UserService.delete_user(target_user.id, mock_user)

    def test_validate_role_valid(self):
        # Given: Valid role string
        # When/Then: No exception raised
        assert UserService.validate_role("field_officer") is True
        assert UserService.validate_role("lga_coordinator") is True
        assert UserService.validate_role("state_admin") is True
        assert UserService.validate_role("super_admin") is True

    def test_validate_role_invalid(self):
        # Given: Invalid role string
        # When/Then: InvalidRoleError raised
        with pytest.raises(InvalidRoleError):
            UserService.validate_role("invalid_role")

        with pytest.raises(InvalidRoleError):
            UserService.validate_role("")

    def test_can_access_lga_field_officer_same(self, mock_user):
        # Given: Field officer checking own LGA
        # When/Then: Returns True
        assert UserService.can_access_lga(mock_user, mock_user.lga_id) is True

    def test_can_access_lga_field_officer_different(self, mock_user):
        # Given: Field officer checking different LGA
        other_lga_id = uuid4()
        # When/Then: Returns False
        assert UserService.can_access_lga(mock_user, other_lga_id) is False

    def test_can_access_lga_state_admin(self, state_admin_user):
        # Given: State admin checking any LGA
        any_lga_id = uuid4()
        # When/Then: Returns True (state-wide access)
        assert UserService.can_access_lga(state_admin_user, any_lga_id) is True

    def test_can_access_lga_super_admin(self, super_admin_user):
        # Given: Super admin checking any LGA
        any_lga_id = uuid4()
        # When/Then: Returns True (full access)
        assert UserService.can_access_lga(super_admin_user, any_lga_id) is True
