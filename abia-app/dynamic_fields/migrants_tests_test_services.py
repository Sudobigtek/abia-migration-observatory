"""Unit tests for migrants.services module.

Tests cover:
- MigrantService: CRUD operations, RLS enforcement,
  validation rules, duplicate detection

All tests use mocked repositories to ensure pure unit testing.
"""

from datetime import date
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from common.exceptions import (
    DuplicateMigrantError,
    LGAAccessDenied,
    LGANotFoundError,
    MigrantNotFoundError,
    ValidationError,
)
from migrants.repositories import MigrantRepository
from migrants.services import MigrantService

# ───────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────


@pytest.fixture
def mock_user_field_officer():
    """Return a mocked field officer user."""
    user = MagicMock()
    user.id = uuid4()
    user.role = "field_officer"
    user.lga_id = uuid4()
    user.lga = MagicMock()
    user.lga.name = "Aba North"
    return user


@pytest.fixture
def mock_user_state_admin():
    """Return a mocked state admin user."""
    user = MagicMock()
    user.id = uuid4()
    user.role = "state_admin"
    user.lga_id = uuid4()
    return user


@pytest.fixture
def mock_migrant(mock_user_field_officer):
    """Return a mocked Migrant object."""
    migrant = MagicMock()
    migrant.id = uuid4()
    migrant.full_name = "John Doe"
    migrant.phone = "+2348012345678"
    migrant.date_of_birth = date(1990, 5, 15)
    migrant.current_lga_id = mock_user_field_officer.lga_id
    migrant.lga_of_origin_id = uuid4()
    migrant.status = "active"
    migrant.created_at = "2026-07-01T10:00:00Z"
    return migrant


@pytest.fixture
def valid_migrant_data(mock_user_field_officer):
    """Return valid migrant creation data."""
    return {
        "full_name": "Jane Smith",
        "phone": "+2348098765432",
        "date_of_birth": date(1985, 3, 20),
        "current_lga_id": str(mock_user_field_officer.lga_id),
        "lga_of_origin_id": str(uuid4()),
        "status": "active",
    }


# ───────────────────────────────────────────────────────────────
# MigrantService — List / Retrieve Tests
# ───────────────────────────────────────────────────────────────


class TestMigrantServiceListRetrieve:
    """Test suite for MigrantService list and retrieve operations."""

    def test_get_migrants_for_request_field_officer(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Field officer with assigned LGA
        with patch.object(
            MigrantRepository, "get_by_lga", return_value=[mock_migrant]
        ) as mock_repo:
            # When: Service retrieves migrants for field officer
            result = MigrantService.get_migrants_for_request(mock_user_field_officer)

            # Then: Only own LGA migrants returned
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
            assert result[0].full_name == "John Doe"

    def test_get_migrants_for_request_state_admin(
        self, mock_user_state_admin, mock_migrant
    ):
        # Given: State admin
        with patch.object(
            MigrantRepository, "get_all", return_value=[mock_migrant]
        ) as mock_repo:
            # When: Service retrieves migrants for state admin
            result = MigrantService.get_migrants_for_request(mock_user_state_admin)

            # Then: All migrants returned (state-wide access)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_migrant_by_id_found_same_lga(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Migrant exists in officer's LGA
        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ) as mock_repo:
            # When: Service retrieves migrant
            result = MigrantService.get_migrant_by_id(
                mock_migrant.id, mock_user_field_officer
            )

            # Then: Migrant returned
            mock_repo.assert_called_once_with(mock_migrant.id)
            assert result == mock_migrant

    def test_get_migrant_by_id_not_found(self, mock_user_field_officer):
        # Given: Migrant ID does not exist
        migrant_id = uuid4()
        with patch.object(
            MigrantRepository, "get_by_id", return_value=None
        ) as mock_repo:
            # When/Then: MigrantNotFoundError raised
            with pytest.raises(MigrantNotFoundError):
                MigrantService.get_migrant_by_id(migrant_id, mock_user_field_officer)

            mock_repo.assert_called_once_with(migrant_id)

    def test_get_migrant_by_id_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Migrant exists in different LGA
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()  # Different from officer's LGA

        with patch.object(MigrantRepository, "get_by_id", return_value=other_migrant):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                MigrantService.get_migrant_by_id(
                    other_migrant.id, mock_user_field_officer
                )

    def test_get_migrant_by_id_state_admin_other_lga(self, mock_user_state_admin):
        # Given: Migrant in different LGA, but requester is state admin
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()

        with patch.object(
            MigrantRepository, "get_by_id", return_value=other_migrant
        ) as mock_repo:
            # When: State admin retrieves migrant
            result = MigrantService.get_migrant_by_id(
                other_migrant.id, mock_user_state_admin
            )

            # Then: Access granted (state-wide)
            mock_repo.assert_called_once_with(other_migrant.id)
            assert result == other_migrant


# ───────────────────────────────────────────────────────────────
# MigrantService — Create Tests
# ───────────────────────────────────────────────────────────────


class TestMigrantServiceCreate:
    """Test suite for MigrantService create operations with validation."""

    def test_create_migrant_field_officer_same_lga(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Field officer creating migrant in own LGA
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.full_name = valid_migrant_data["full_name"]

        with patch.object(
            MigrantRepository, "get_by_phone", return_value=None
        ), patch.object(
            MigrantRepository, "create", return_value=mock_created
        ) as mock_create:
            # When: Service creates migrant
            result = MigrantService.create_migrant(
                valid_migrant_data, mock_user_field_officer
            )

            # Then: Migrant created successfully
            mock_create.assert_called_once()
            assert result.full_name == "Jane Smith"

    def test_create_migrant_field_officer_different_lga(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Field officer creating migrant in different LGA
        valid_migrant_data["current_lga_id"] = str(uuid4())  # Different LGA

        # When/Then: Access denied
        with pytest.raises(LGAAccessDenied) as exc_info:
            MigrantService.create_migrant(valid_migrant_data, mock_user_field_officer)

        assert "outside your LGA" in str(exc_info.value).lower()

    def test_create_migrant_state_admin_any_lga(
        self, mock_user_state_admin, valid_migrant_data
    ):
        # Given: State admin creating migrant in any LGA
        valid_migrant_data["current_lga_id"] = str(uuid4())  # Any LGA
        mock_created = MagicMock()
        mock_created.id = uuid4()

        with patch.object(
            MigrantRepository, "get_by_phone", return_value=None
        ), patch.object(
            MigrantRepository, "create", return_value=mock_created
        ) as mock_create:
            # When: Service creates migrant
            result = MigrantService.create_migrant(
                valid_migrant_data, mock_user_state_admin
            )

            # Then: Migrant created (state admin has cross-LGA access)
            mock_create.assert_called_once()
            assert result is not None

    def test_create_migrant_duplicate_phone(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Phone number already exists
        existing_migrant = MagicMock()
        existing_migrant.phone = valid_migrant_data["phone"]

        with patch.object(
            MigrantRepository, "get_by_phone", return_value=existing_migrant
        ):
            # When/Then: DuplicateMigrantError raised
            with pytest.raises(DuplicateMigrantError) as exc_info:
                MigrantService.create_migrant(
                    valid_migrant_data, mock_user_field_officer
                )

            assert "phone" in str(exc_info.value).lower()

    def test_create_migrant_missing_full_name(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Missing required field full_name
        invalid_data = valid_migrant_data.copy()
        invalid_data["full_name"] = ""

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)

        assert "full_name" in str(exc_info.value).lower()

    def test_create_migrant_missing_phone(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Missing required field phone
        invalid_data = valid_migrant_data.copy()
        invalid_data["phone"] = ""

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)

        assert "phone" in str(exc_info.value).lower()

    def test_create_migrant_invalid_phone_format(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Invalid phone format (not Nigerian)
        invalid_data = valid_migrant_data.copy()
        invalid_data["phone"] = "12345"  # Too short, no country code

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)

        assert "phone" in str(exc_info.value).lower()

    def test_create_migrant_invalid_lga(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Invalid LGA ID (does not exist)
        invalid_data = valid_migrant_data.copy()
        invalid_data["current_lga_id"] = str(uuid4())

        with patch.object(MigrantRepository, "get_by_phone", return_value=None):
            # When/Then: LGAAccessDenied or LGANotFoundError
            with pytest.raises((LGAAccessDenied, LGANotFoundError)):
                MigrantService.create_migrant(invalid_data, mock_user_field_officer)

    def test_create_migrant_future_date_of_birth(
        self, mock_user_field_officer, valid_migrant_data
    ):
        # Given: Future date of birth
        from datetime import datetime, timedelta

        invalid_data = valid_migrant_data.copy()
        invalid_data["date_of_birth"] = datetime.now().date() + timedelta(days=1)

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)

        assert (
            "date" in str(exc_info.value).lower()
            or "future" in str(exc_info.value).lower()
        )


# ───────────────────────────────────────────────────────────────
# MigrantService — Update Tests
# ───────────────────────────────────────────────────────────────


class TestMigrantServiceUpdate:
    """Test suite for MigrantService update operations."""

    def test_update_migrant_field_officer_same_lga(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Field officer updating migrant in own LGA
        update_data = {"full_name": "Updated Name"}
        updated_migrant = MagicMock()
        updated_migrant.full_name = "Updated Name"
        updated_migrant.current_lga_id = mock_user_field_officer.lga_id

        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ), patch.object(
            MigrantRepository, "update", return_value=updated_migrant
        ) as mock_update:
            # When: Service updates migrant
            result = MigrantService.update_migrant(
                mock_migrant.id, update_data, mock_user_field_officer
            )

            # Then: Update succeeds
            mock_update.assert_called_once()
            assert result.full_name == "Updated Name"

    def test_update_migrant_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Migrant in different LGA
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()
        update_data = {"full_name": "Updated Name"}

        with patch.object(MigrantRepository, "get_by_id", return_value=other_migrant):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                MigrantService.update_migrant(
                    other_migrant.id, update_data, mock_user_field_officer
                )

    def test_update_migrant_not_found(self, mock_user_field_officer):
        # Given: Migrant ID does not exist
        migrant_id = uuid4()
        update_data = {"full_name": "Updated Name"}

        with patch.object(MigrantRepository, "get_by_id", return_value=None):
            # When/Then: MigrantNotFoundError raised
            with pytest.raises(MigrantNotFoundError):
                MigrantService.update_migrant(
                    migrant_id, update_data, mock_user_field_officer
                )

    def test_update_migrant_status_transition_valid(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Valid status transition (active -> inactive)
        update_data = {"status": "inactive"}
        updated_migrant = MagicMock()
        updated_migrant.status = "inactive"
        updated_migrant.current_lga_id = mock_user_field_officer.lga_id

        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ), patch.object(
            MigrantRepository, "update", return_value=updated_migrant
        ) as mock_update:
            # When: Service updates status
            result = MigrantService.update_migrant(
                mock_migrant.id, update_data, mock_user_field_officer
            )

            # Then: Status updated
            mock_update.assert_called_once()
            assert result.status == "inactive"

    def test_update_migrant_status_transition_invalid(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Invalid status transition (active -> deleted - not allowed for field officer)
        update_data = {"status": "deleted"}

        with patch.object(MigrantRepository, "get_by_id", return_value=mock_migrant):
            # When/Then: ValidationError or LGAAccessDenied
            with pytest.raises((ValidationError, LGAAccessDenied)):
                MigrantService.update_migrant(
                    mock_migrant.id, update_data, mock_user_field_officer
                )


# ───────────────────────────────────────────────────────────────
# MigrantService — Delete Tests
# ───────────────────────────────────────────────────────────────


class TestMigrantServiceDelete:
    """Test suite for MigrantService delete operations."""

    def test_delete_migrant_field_officer_same_lga(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Field officer deleting migrant in own LGA
        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ), patch.object(MigrantRepository, "delete", return_value=True) as mock_delete:
            # When: Service deletes migrant
            result = MigrantService.delete_migrant(
                mock_migrant.id, mock_user_field_officer
            )

            # Then: Delete succeeds
            mock_delete.assert_called_once()
            assert result is True

    def test_delete_migrant_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Migrant in different LGA
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()

        with patch.object(MigrantRepository, "get_by_id", return_value=other_migrant):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                MigrantService.delete_migrant(other_migrant.id, mock_user_field_officer)

    def test_delete_migrant_state_admin_any_lga(self, mock_user_state_admin):
        # Given: State admin deleting migrant in any LGA
        any_migrant = MagicMock()
        any_migrant.id = uuid4()
        any_migrant.current_lga_id = uuid4()

        with patch.object(
            MigrantRepository, "get_by_id", return_value=any_migrant
        ), patch.object(MigrantRepository, "delete", return_value=True) as mock_delete:
            # When: Service deletes migrant
            result = MigrantService.delete_migrant(
                any_migrant.id, mock_user_state_admin
            )

            # Then: Delete succeeds (state admin has cross-LGA access)
            mock_delete.assert_called_once()
            assert result is True

    def test_delete_migrant_not_found(self, mock_user_field_officer):
        # Given: Migrant ID does not exist
        migrant_id = uuid4()

        with patch.object(MigrantRepository, "get_by_id", return_value=None):
            # When/Then: MigrantNotFoundError raised
            with pytest.raises(MigrantNotFoundError):
                MigrantService.delete_migrant(migrant_id, mock_user_field_officer)


# ───────────────────────────────────────────────────────────────
# MigrantService — Search & Filter Tests
# ───────────────────────────────────────────────────────────────


class TestMigrantServiceSearch:
    """Test suite for MigrantService search and filter operations."""

    def test_search_by_name_field_officer(self, mock_user_field_officer, mock_migrant):
        # Given: Field officer searching by name in own LGA
        with patch.object(
            MigrantRepository, "search_by_name_in_lga", return_value=[mock_migrant]
        ) as mock_repo:
            # When: Service searches migrants
            result = MigrantService.search_migrants_by_name(
                "John", mock_user_field_officer
            )

            # Then: Only own LGA results returned
            mock_repo.assert_called_once_with("John", mock_user_field_officer.lga_id)
            assert len(result) == 1

    def test_search_by_name_state_admin(self, mock_user_state_admin, mock_migrant):
        # Given: State admin searching by name
        with patch.object(
            MigrantRepository, "search_by_name", return_value=[mock_migrant]
        ) as mock_repo:
            # When: Service searches migrants
            result = MigrantService.search_migrants_by_name(
                "John", mock_user_state_admin
            )

            # Then: State-wide search performed
            mock_repo.assert_called_once_with("John")
            assert len(result) == 1

    def test_filter_by_status_field_officer(
        self, mock_user_field_officer, mock_migrant
    ):
        # Given: Field officer filtering by status
        with patch.object(
            MigrantRepository, "filter_by_status_in_lga", return_value=[mock_migrant]
        ) as mock_repo:
            # When: Service filters migrants
            result = MigrantService.filter_migrants_by_status(
                "active", mock_user_field_officer
            )

            # Then: Only own LGA results returned
            mock_repo.assert_called_once_with("active", mock_user_field_officer.lga_id)
            assert len(result) == 1

    def test_count_migrants_by_lga_field_officer(self, mock_user_field_officer):
        # Given: Field officer requesting count
        with patch.object(
            MigrantRepository, "count_by_lga", return_value=42
        ) as mock_repo:
            # When: Service counts migrants
            result = MigrantService.count_migrants_by_lga(
                mock_user_field_officer.lga_id, mock_user_field_officer
            )

            # Then: Count returned for own LGA
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert result == 42

    def test_count_migrants_by_lga_field_officer_other_lga(
        self, mock_user_field_officer
    ):
        # Given: Field officer requesting count for different LGA
        other_lga_id = uuid4()

        # When/Then: Access denied
        with pytest.raises(LGAAccessDenied):
            MigrantService.count_migrants_by_lga(other_lga_id, mock_user_field_officer)
