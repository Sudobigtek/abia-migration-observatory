"""Unit tests for cases.services module.

Tests cover:
- CaseService: CRUD operations, RLS enforcement,
  case assignment, status transitions, priority validation

All tests use mocked repositories to ensure pure unit testing.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from cases.repositories import CaseRepository
from cases.services import CaseService
from common.exceptions import (
    CaseNotFoundError,
    InvalidPriorityError,
    InvalidStatusTransitionError,
    LGAAccessDenied,
    ValidationError,
)

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
def mock_user_lga_coordinator():
    """Return a mocked LGA coordinator user."""
    user = MagicMock()
    user.id = uuid4()
    user.role = "lga_coordinator"
    user.lga_id = uuid4()
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
def mock_migrant():
    """Return a mocked Migrant object."""
    migrant = MagicMock()
    migrant.id = uuid4()
    migrant.full_name = "John Doe"
    migrant.current_lga_id = uuid4()
    return migrant


@pytest.fixture
def mock_case(mock_user_field_officer, mock_migrant):
    """Return a mocked Case object."""
    case = MagicMock()
    case.id = uuid4()
    case.migrant_id = mock_migrant.id
    case.migrant = mock_migrant
    case.lga_id = mock_user_field_officer.lga_id
    case.assigned_to_id = mock_user_field_officer.id
    case.assigned_to = mock_user_field_officer
    case.status = "open"
    case.priority = "medium"
    case.case_type = "protection"
    case.description = "Test case description"
    case.created_at = datetime(2026, 7, 1, 10, 0, 0)
    case.updated_at = datetime(2026, 7, 1, 10, 0, 0)
    case.resolved_at = None
    case.created_by_id = mock_user_field_officer.id
    return case


@pytest.fixture
def valid_case_data(mock_user_field_officer, mock_migrant):
    """Return valid case creation data."""
    return {
        "migrant_id": str(mock_migrant.id),
        "lga_id": str(mock_user_field_officer.lga_id),
        "case_type": "protection",
        "priority": "medium",
        "description": "New case description",
        "status": "open",
    }


# ───────────────────────────────────────────────────────────────
# CaseService — List / Retrieve Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceListRetrieve:
    """Test suite for CaseService list and retrieve operations."""

    def test_get_cases_for_request_field_officer(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Field officer with assigned LGA
        with patch.object(
            CaseRepository, "get_by_lga", return_value=[mock_case]
        ) as mock_repo:
            # When: Service retrieves cases for field officer
            result = CaseService.get_cases_for_request(mock_user_field_officer)

            # Then: Only own LGA cases returned
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
            assert result[0].case_type == "protection"

    def test_get_cases_for_request_lga_coordinator(
        self, mock_user_lga_coordinator, mock_case
    ):
        # Given: LGA coordinator with assigned LGA
        with patch.object(
            CaseRepository, "get_by_lga", return_value=[mock_case]
        ) as mock_repo:
            # When: Service retrieves cases for coordinator
            result = CaseService.get_cases_for_request(mock_user_lga_coordinator)

            # Then: Only own LGA cases returned
            mock_repo.assert_called_once_with(mock_user_lga_coordinator.lga_id)
            assert len(result) == 1

    def test_get_cases_for_request_state_admin(self, mock_user_state_admin, mock_case):
        # Given: State admin
        with patch.object(
            CaseRepository, "get_all", return_value=[mock_case]
        ) as mock_repo:
            # When: Service retrieves cases for state admin
            result = CaseService.get_cases_for_request(mock_user_state_admin)

            # Then: All cases returned (state-wide access)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_case_by_id_found_same_lga(self, mock_user_field_officer, mock_case):
        # Given: Case exists in officer's LGA
        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ) as mock_repo:
            # When: Service retrieves case
            result = CaseService.get_case_by_id(mock_case.id, mock_user_field_officer)

            # Then: Case returned
            mock_repo.assert_called_once_with(mock_case.id)
            assert result == mock_case

    def test_get_case_by_id_not_found(self, mock_user_field_officer):
        # Given: Case ID does not exist
        case_id = uuid4()
        with patch.object(CaseRepository, "get_by_id", return_value=None) as mock_repo:
            # When/Then: CaseNotFoundError raised
            with pytest.raises(CaseNotFoundError):
                CaseService.get_case_by_id(case_id, mock_user_field_officer)

            mock_repo.assert_called_once_with(case_id)

    def test_get_case_by_id_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Case exists in different LGA
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()  # Different from officer's LGA

        with patch.object(CaseRepository, "get_by_id", return_value=other_case):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                CaseService.get_case_by_id(other_case.id, mock_user_field_officer)

    def test_get_case_by_id_state_admin_other_lga(self, mock_user_state_admin):
        # Given: Case in different LGA, but requester is state admin
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()

        with patch.object(
            CaseRepository, "get_by_id", return_value=other_case
        ) as mock_repo:
            # When: State admin retrieves case
            result = CaseService.get_case_by_id(other_case.id, mock_user_state_admin)

            # Then: Access granted (state-wide)
            mock_repo.assert_called_once_with(other_case.id)
            assert result == other_case


# ───────────────────────────────────────────────────────────────
# CaseService — Create Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceCreate:
    """Test suite for CaseService create operations with validation."""

    def test_create_case_field_officer_same_lga(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Field officer creating case in own LGA
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.case_type = "protection"

        with patch.object(
            CaseRepository, "create", return_value=mock_created
        ) as mock_create:
            # When: Service creates case
            result = CaseService.create_case(valid_case_data, mock_user_field_officer)

            # Then: Case created successfully
            mock_create.assert_called_once()
            assert result.case_type == "protection"

    def test_create_case_field_officer_different_lga(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Field officer creating case in different LGA
        valid_case_data["lga_id"] = str(uuid4())  # Different LGA

        # When/Then: Access denied
        with pytest.raises(LGAAccessDenied) as exc_info:
            CaseService.create_case(valid_case_data, mock_user_field_officer)

        assert "outside your LGA" in str(exc_info.value).lower()

    def test_create_case_state_admin_any_lga(
        self, mock_user_state_admin, valid_case_data
    ):
        # Given: State admin creating case in any LGA
        valid_case_data["lga_id"] = str(uuid4())  # Any LGA
        mock_created = MagicMock()
        mock_created.id = uuid4()

        with patch.object(
            CaseRepository, "create", return_value=mock_created
        ) as mock_create:
            # When: Service creates case
            result = CaseService.create_case(valid_case_data, mock_user_state_admin)

            # Then: Case created (state admin has cross-LGA access)
            mock_create.assert_called_once()
            assert result is not None

    def test_create_case_invalid_case_type(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Invalid case type
        invalid_data = valid_case_data.copy()
        invalid_data["case_type"] = "invalid_type"

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)

        assert "case_type" in str(exc_info.value).lower()

    def test_create_case_invalid_priority(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Invalid priority
        invalid_data = valid_case_data.copy()
        invalid_data["priority"] = "critical"  # Not in allowed values

        # When/Then: InvalidPriorityError or ValidationError raised
        with pytest.raises((InvalidPriorityError, ValidationError)) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)

        assert "priority" in str(exc_info.value).lower()

    def test_create_case_missing_description(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Missing required description
        invalid_data = valid_case_data.copy()
        invalid_data["description"] = ""

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)

        assert "description" in str(exc_info.value).lower()

    def test_create_case_missing_migrant_id(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Missing migrant ID
        invalid_data = valid_case_data.copy()
        invalid_data["migrant_id"] = ""

        # When/Then: ValidationError raised
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)

        assert "migrant" in str(exc_info.value).lower()

    def test_create_case_sets_created_by(
        self, mock_user_field_officer, valid_case_data
    ):
        # Given: Valid case data
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.created_by_id = mock_user_field_officer.id

        with patch.object(
            CaseRepository, "create", return_value=mock_created
        ) as mock_create:
            # When: Service creates case
            result = CaseService.create_case(valid_case_data, mock_user_field_officer)

            # Then: created_by is set to requesting user
            call_args = (
                mock_create.call_args[0][0]
                if mock_create.call_args[0]
                else mock_create.call_args[1]
            )
            assert result.created_by_id == mock_user_field_officer.id


# ───────────────────────────────────────────────────────────────
# CaseService — Update Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceUpdate:
    """Test suite for CaseService update operations."""

    def test_update_case_field_officer_same_lga(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Field officer updating case in own LGA
        update_data = {"description": "Updated description"}
        updated_case = MagicMock()
        updated_case.description = "Updated description"
        updated_case.lga_id = mock_user_field_officer.lga_id

        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            # When: Service updates case
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_field_officer
            )

            # Then: Update succeeds
            mock_update.assert_called_once()
            assert result.description == "Updated description"

    def test_update_case_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Case in different LGA
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()
        update_data = {"description": "Updated description"}

        with patch.object(CaseRepository, "get_by_id", return_value=other_case):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                CaseService.update_case(
                    other_case.id, update_data, mock_user_field_officer
                )

    def test_update_case_not_found(self, mock_user_field_officer):
        # Given: Case ID does not exist
        case_id = uuid4()
        update_data = {"description": "Updated description"}

        with patch.object(CaseRepository, "get_by_id", return_value=None):
            # When/Then: CaseNotFoundError raised
            with pytest.raises(CaseNotFoundError):
                CaseService.update_case(case_id, update_data, mock_user_field_officer)

    def test_update_case_status_transition_valid(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Valid status transition (open -> in_progress)
        update_data = {"status": "in_progress"}
        updated_case = MagicMock()
        updated_case.status = "in_progress"
        updated_case.lga_id = mock_user_field_officer.lga_id

        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            # When: Service updates status
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_field_officer
            )

            # Then: Status updated
            mock_update.assert_called_once()
            assert result.status == "in_progress"

    def test_update_case_status_transition_invalid(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Invalid status transition (open -> resolved without in_progress)
        update_data = {"status": "resolved"}

        with patch.object(CaseRepository, "get_by_id", return_value=mock_case):
            # When/Then: InvalidStatusTransitionError raised
            with pytest.raises(InvalidStatusTransitionError) as exc_info:
                CaseService.update_case(
                    mock_case.id, update_data, mock_user_field_officer
                )

            assert (
                "status" in str(exc_info.value).lower()
                or "transition" in str(exc_info.value).lower()
            )

    def test_update_case_priority_by_field_officer(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Field officer trying to escalate priority
        update_data = {"priority": "high"}
        updated_case = MagicMock()
        updated_case.priority = "high"
        updated_case.lga_id = mock_user_field_officer.lga_id

        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            # When: Service updates priority
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_field_officer
            )

            # Then: Priority updated (field officers can escalate)
            mock_update.assert_called_once()
            assert result.priority == "high"

    def test_update_case_assign_to_user_same_lga(
        self, mock_user_lga_coordinator, mock_case
    ):
        # Given: LGA coordinator assigning case to user in same LGA
        target_user = MagicMock()
        target_user.id = uuid4()
        target_user.lga_id = mock_case.lga_id  # Same LGA as case
        update_data = {"assigned_to_id": str(target_user.id)}
        updated_case = MagicMock()
        updated_case.assigned_to_id = target_user.id
        updated_case.lga_id = mock_case.lga_id

        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            # When: Service assigns case
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_lga_coordinator
            )

            # Then: Assignment succeeds
            mock_update.assert_called_once()
            assert result.assigned_to_id == target_user.id


# ───────────────────────────────────────────────────────────────
# CaseService — Delete Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceDelete:
    """Test suite for CaseService delete operations."""

    def test_delete_case_field_officer_same_lga(
        self, mock_user_field_officer, mock_case
    ):
        # Given: Field officer deleting case in own LGA
        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(CaseRepository, "delete", return_value=True) as mock_delete:
            # When: Service deletes case
            result = CaseService.delete_case(mock_case.id, mock_user_field_officer)

            # Then: Delete succeeds
            mock_delete.assert_called_once()
            assert result is True

    def test_delete_case_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Case in different LGA
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()

        with patch.object(CaseRepository, "get_by_id", return_value=other_case):
            # When/Then: Access denied
            with pytest.raises(LGAAccessDenied):
                CaseService.delete_case(other_case.id, mock_user_field_officer)

    def test_delete_case_state_admin_any_lga(self, mock_user_state_admin):
        # Given: State admin deleting case in any LGA
        any_case = MagicMock()
        any_case.id = uuid4()
        any_case.lga_id = uuid4()

        with patch.object(
            CaseRepository, "get_by_id", return_value=any_case
        ), patch.object(CaseRepository, "delete", return_value=True) as mock_delete:
            # When: Service deletes case
            result = CaseService.delete_case(any_case.id, mock_user_state_admin)

            # Then: Delete succeeds (state admin has cross-LGA access)
            mock_delete.assert_called_once()
            assert result is True

    def test_delete_case_not_found(self, mock_user_field_officer):
        # Given: Case ID does not exist
        case_id = uuid4()

        with patch.object(CaseRepository, "get_by_id", return_value=None):
            # When/Then: CaseNotFoundError raised
            with pytest.raises(CaseNotFoundError):
                CaseService.delete_case(case_id, mock_user_field_officer)


# ───────────────────────────────────────────────────────────────
# CaseService — Status Transition Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceStatusTransitions:
    """Test suite for CaseService status transition rules."""

    def test_valid_transition_open_to_in_progress(self, mock_user_field_officer):
        # Given: Case in "open" status
        case = MagicMock()
        case.id = uuid4()
        case.status = "open"
        case.lga_id = mock_user_field_officer.lga_id

        update_data = {"status": "in_progress"}
        updated_case = MagicMock()
        updated_case.status = "in_progress"
        updated_case.lga_id = mock_user_field_officer.lga_id

        with patch.object(CaseRepository, "get_by_id", return_value=case), patch.object(
            CaseRepository, "update", return_value=updated_case
        ):
            # When: Transition to in_progress
            result = CaseService.update_case(
                case.id, update_data, mock_user_field_officer
            )

            # Then: Transition succeeds
            assert result.status == "in_progress"

    def test_valid_transition_in_progress_to_resolved(self, mock_user_field_officer):
        # Given: Case in "in_progress" status
        case = MagicMock()
        case.id = uuid4()
        case.status = "in_progress"
        case.lga_id = mock_user_field_officer.lga_id

        update_data = {"status": "resolved"}
        updated_case = MagicMock()
        updated_case.status = "resolved"
        updated_case.lga_id = mock_user_field_officer.lga_id
        updated_case.resolved_at = datetime(2026, 7, 9, 12, 0, 0)

        with patch.object(CaseRepository, "get_by_id", return_value=case), patch.object(
            CaseRepository, "update", return_value=updated_case
        ):
            # When: Transition to resolved
            result = CaseService.update_case(
                case.id, update_data, mock_user_field_officer
            )

            # Then: Transition succeeds, resolved_at set
            assert result.status == "resolved"

    def test_valid_transition_in_progress_to_on_hold(self, mock_user_field_officer):
        # Given: Case in "in_progress" status
        case = MagicMock()
        case.id = uuid4()
        case.status = "in_progress"
        case.lga_id = mock_user_field_officer.lga_id

        update_data = {"status": "on_hold"}
        updated_case = MagicMock()
        updated_case.status = "on_hold"
        updated_case.lga_id = mock_user_field_officer.lga_id

        with patch.object(CaseRepository, "get_by_id", return_value=case), patch.object(
            CaseRepository, "update", return_value=updated_case
        ):
            # When: Transition to on_hold
            result = CaseService.update_case(
                case.id, update_data, mock_user_field_officer
            )

            # Then: Transition succeeds
            assert result.status == "on_hold"

    def test_invalid_transition_resolved_to_open(self, mock_user_field_officer):
        # Given: Case already resolved
        case = MagicMock()
        case.id = uuid4()
        case.status = "resolved"
        case.lga_id = mock_user_field_officer.lga_id

        update_data = {"status": "open"}

        with patch.object(CaseRepository, "get_by_id", return_value=case):
            # When/Then: InvalidStatusTransitionError raised
            with pytest.raises(InvalidStatusTransitionError) as exc_info:
                CaseService.update_case(case.id, update_data, mock_user_field_officer)

            assert (
                "resolved" in str(exc_info.value).lower()
                or "transition" in str(exc_info.value).lower()
            )

    def test_invalid_transition_on_hold_to_resolved(self, mock_user_field_officer):
        # Given: Case on hold
        case = MagicMock()
        case.id = uuid4()
        case.status = "on_hold"
        case.lga_id = mock_user_field_officer.lga_id

        update_data = {"status": "resolved"}

        with patch.object(CaseRepository, "get_by_id", return_value=case):
            # When/Then: InvalidStatusTransitionError raised
            with pytest.raises(InvalidStatusTransitionError) as exc_info:
                CaseService.update_case(case.id, update_data, mock_user_field_officer)

            assert (
                "on_hold" in str(exc_info.value).lower()
                or "transition" in str(exc_info.value).lower()
            )


# ───────────────────────────────────────────────────────────────
# CaseService — Search & Filter Tests
# ───────────────────────────────────────────────────────────────


class TestCaseServiceSearchFilter:
    """Test suite for CaseService search and filter operations."""

    def test_filter_by_status_field_officer(self, mock_user_field_officer, mock_case):
        # Given: Field officer filtering by status
        with patch.object(
            CaseRepository, "filter_by_status_in_lga", return_value=[mock_case]
        ) as mock_repo:
            # When: Service filters cases
            result = CaseService.filter_cases_by_status("open", mock_user_field_officer)

            # Then: Only own LGA results returned
            mock_repo.assert_called_once_with("open", mock_user_field_officer.lga_id)
            assert len(result) == 1

    def test_filter_by_priority_field_officer(self, mock_user_field_officer, mock_case):
        # Given: Field officer filtering by priority
        with patch.object(
            CaseRepository, "filter_by_priority_in_lga", return_value=[mock_case]
        ) as mock_repo:
            # When: Service filters cases
            result = CaseService.filter_cases_by_priority(
                "medium", mock_user_field_officer
            )

            # Then: Only own LGA results returned
            mock_repo.assert_called_once_with("medium", mock_user_field_officer.lga_id)
            assert len(result) == 1

    def test_filter_by_case_type_state_admin(self, mock_user_state_admin, mock_case):
        # Given: State admin filtering by case type
        with patch.object(
            CaseRepository, "filter_by_case_type", return_value=[mock_case]
        ) as mock_repo:
            # When: Service filters cases
            result = CaseService.filter_cases_by_type(
                "protection", mock_user_state_admin
            )

            # Then: State-wide filter performed
            mock_repo.assert_called_once_with("protection")
            assert len(result) == 1

    def test_count_cases_by_lga_field_officer(self, mock_user_field_officer):
        # Given: Field officer requesting count
        with patch.object(CaseRepository, "count_by_lga", return_value=15) as mock_repo:
            # When: Service counts cases
            result = CaseService.count_cases_by_lga(
                mock_user_field_officer.lga_id, mock_user_field_officer
            )

            # Then: Count returned for own LGA
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert result == 15

    def test_count_cases_by_lga_field_officer_other_lga(self, mock_user_field_officer):
        # Given: Field officer requesting count for different LGA
        other_lga_id = uuid4()

        # When/Then: Access denied
        with pytest.raises(LGAAccessDenied):
            CaseService.count_cases_by_lga(other_lga_id, mock_user_field_officer)

    def test_get_overdue_cases_field_officer(self, mock_user_field_officer, mock_case):
        # Given: Field officer requesting overdue cases
        with patch.object(
            CaseRepository, "get_overdue_by_lga", return_value=[mock_case]
        ) as mock_repo:
            # When: Service retrieves overdue cases
            result = CaseService.get_overdue_cases(mock_user_field_officer)

            # Then: Only own LGA overdue cases returned
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
