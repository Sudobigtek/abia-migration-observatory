"""Unit tests for abia.cases.services module.

Tests use mocked repositories (abia.cases.repositories).
Matches actual repository methods: create, get_all, get_by_id, get_by_lga, get_by_migrant, update

Per Architecture Contract §8.1: Unit tests = 80% of pyramid.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from abia.cases.repositories import CaseRepository
from abia.cases.services import CaseService
from common.exceptions import (
    CaseNotFoundError,
    InvalidPriorityError,
    InvalidStatusTransitionError,
    LGAAccessDenied,
    ValidationError,
)


@pytest.fixture
def mock_user_field_officer():
    user = MagicMock()
    user.id = uuid4()
    user.role = "field_officer"
    user.lga_id = uuid4()
    user.lga = MagicMock()
    user.lga.name = "Aba North"
    return user


@pytest.fixture
def mock_user_state_admin():
    user = MagicMock()
    user.id = uuid4()
    user.role = "state_admin"
    user.lga_id = uuid4()
    return user


@pytest.fixture
def mock_migrant():
    migrant = MagicMock()
    migrant.id = uuid4()
    migrant.full_name = "John Doe"
    migrant.current_lga_id = uuid4()
    return migrant


@pytest.fixture
def mock_case(mock_user_field_officer, mock_migrant):
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
    return {
        "migrant_id": str(mock_migrant.id),
        "lga_id": str(mock_user_field_officer.lga_id),
        "case_type": "protection",
        "priority": "medium",
        "description": "New case description",
        "status": "open",
    }


class TestCaseServiceListRetrieve:
    def test_get_cases_for_request_field_officer(
        self, mock_user_field_officer, mock_case
    ):
        with patch.object(
            CaseRepository, "get_by_lga", return_value=[mock_case]
        ) as mock_repo:
            result = CaseService.get_cases_for_request(mock_user_field_officer)
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
            assert result[0].case_type == "protection"

    def test_get_cases_for_request_state_admin(self, mock_user_state_admin, mock_case):
        with patch.object(
            CaseRepository, "get_all", return_value=[mock_case]
        ) as mock_repo:
            result = CaseService.get_cases_for_request(mock_user_state_admin)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_case_by_id_found_same_lga(self, mock_user_field_officer, mock_case):
        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ) as mock_repo:
            result = CaseService.get_case_by_id(mock_case.id, mock_user_field_officer)
            mock_repo.assert_called_once_with(mock_case.id)
            assert result == mock_case

    def test_get_case_by_id_not_found(self, mock_user_field_officer):
        case_id = uuid4()
        with patch.object(CaseRepository, "get_by_id", return_value=None) as mock_repo:
            with pytest.raises(CaseNotFoundError):
                CaseService.get_case_by_id(case_id, mock_user_field_officer)
            mock_repo.assert_called_once_with(case_id)

    def test_get_case_by_id_field_officer_other_lga(self, mock_user_field_officer):
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()
        with patch.object(CaseRepository, "get_by_id", return_value=other_case):
            with pytest.raises(LGAAccessDenied):
                CaseService.get_case_by_id(other_case.id, mock_user_field_officer)

    def test_get_case_by_id_state_admin_other_lga(self, mock_user_state_admin):
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()
        with patch.object(
            CaseRepository, "get_by_id", return_value=other_case
        ) as mock_repo:
            result = CaseService.get_case_by_id(other_case.id, mock_user_state_admin)
            mock_repo.assert_called_once_with(other_case.id)
            assert result == other_case


class TestCaseServiceCreate:
    def test_create_case_field_officer_same_lga(
        self, mock_user_field_officer, valid_case_data
    ):
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.case_type = "protection"
        with patch.object(
            CaseRepository, "create", return_value=mock_created
        ) as mock_create:
            result = CaseService.create_case(valid_case_data, mock_user_field_officer)
            mock_create.assert_called_once()
            assert result.case_type == "protection"

    def test_create_case_field_officer_different_lga(
        self, mock_user_field_officer, valid_case_data
    ):
        valid_case_data["lga_id"] = str(uuid4())
        with pytest.raises(LGAAccessDenied) as exc_info:
            CaseService.create_case(valid_case_data, mock_user_field_officer)
        assert "outside your LGA" in str(exc_info.value).lower()

    def test_create_case_state_admin_any_lga(
        self, mock_user_state_admin, valid_case_data
    ):
        valid_case_data["lga_id"] = str(uuid4())
        mock_created = MagicMock()
        mock_created.id = uuid4()
        with patch.object(
            CaseRepository, "create", return_value=mock_created
        ) as mock_create:
            result = CaseService.create_case(valid_case_data, mock_user_state_admin)
            mock_create.assert_called_once()
            assert result is not None

    def test_create_case_invalid_case_type(
        self, mock_user_field_officer, valid_case_data
    ):
        invalid_data = valid_case_data.copy()
        invalid_data["case_type"] = "invalid_type"
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)
        assert "case_type" in str(exc_info.value).lower()

    def test_create_case_invalid_priority(
        self, mock_user_field_officer, valid_case_data
    ):
        invalid_data = valid_case_data.copy()
        invalid_data["priority"] = "critical"
        with pytest.raises((InvalidPriorityError, ValidationError)) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)
        assert "priority" in str(exc_info.value).lower()

    def test_create_case_missing_description(
        self, mock_user_field_officer, valid_case_data
    ):
        invalid_data = valid_case_data.copy()
        invalid_data["description"] = ""
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)
        assert "description" in str(exc_info.value).lower()

    def test_create_case_missing_migrant_id(
        self, mock_user_field_officer, valid_case_data
    ):
        invalid_data = valid_case_data.copy()
        invalid_data["migrant_id"] = ""
        with pytest.raises(ValidationError) as exc_info:
            CaseService.create_case(invalid_data, mock_user_field_officer)
        assert "migrant" in str(exc_info.value).lower()


class TestCaseServiceUpdate:
    def test_update_case_field_officer_same_lga(
        self, mock_user_field_officer, mock_case
    ):
        update_data = {"description": "Updated description"}
        updated_case = MagicMock()
        updated_case.description = "Updated description"
        updated_case.lga_id = mock_user_field_officer.lga_id
        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_field_officer
            )
            mock_update.assert_called_once()
            assert result.description == "Updated description"

    def test_update_case_field_officer_other_lga(self, mock_user_field_officer):
        other_case = MagicMock()
        other_case.id = uuid4()
        other_case.lga_id = uuid4()
        update_data = {"description": "Updated description"}
        with patch.object(CaseRepository, "get_by_id", return_value=other_case):
            with pytest.raises(LGAAccessDenied):
                CaseService.update_case(
                    other_case.id, update_data, mock_user_field_officer
                )

    def test_update_case_not_found(self, mock_user_field_officer):
        case_id = uuid4()
        update_data = {"description": "Updated description"}
        with patch.object(CaseRepository, "get_by_id", return_value=None):
            with pytest.raises(CaseNotFoundError):
                CaseService.update_case(case_id, update_data, mock_user_field_officer)

    def test_update_case_status_transition_valid(
        self, mock_user_field_officer, mock_case
    ):
        update_data = {"status": "in_progress"}
        updated_case = MagicMock()
        updated_case.status = "in_progress"
        updated_case.lga_id = mock_user_field_officer.lga_id
        with patch.object(
            CaseRepository, "get_by_id", return_value=mock_case
        ), patch.object(
            CaseRepository, "update", return_value=updated_case
        ) as mock_update:
            result = CaseService.update_case(
                mock_case.id, update_data, mock_user_field_officer
            )
            mock_update.assert_called_once()
            assert result.status == "in_progress"

    def test_update_case_status_transition_invalid(
        self, mock_user_field_officer, mock_case
    ):
        update_data = {"status": "resolved"}
        with patch.object(CaseRepository, "get_by_id", return_value=mock_case):
            with pytest.raises(InvalidStatusTransitionError) as exc_info:
                CaseService.update_case(
                    mock_case.id, update_data, mock_user_field_officer
                )
            assert (
                "status" in str(exc_info.value).lower()
                or "transition" in str(exc_info.value).lower()
            )


class TestCaseServiceCount:
    def test_count_cases_by_lga_field_officer(self, mock_user_field_officer):
        with patch.object(
            CaseRepository, "get_by_lga", return_value=[MagicMock(), MagicMock()]
        ) as mock_repo:
            result = CaseService.count_cases_by_lga(
                mock_user_field_officer.lga_id, mock_user_field_officer
            )
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert result == 2

    def test_count_cases_by_lga_field_officer_other_lga(self, mock_user_field_officer):
        other_lga_id = uuid4()
        with pytest.raises(LGAAccessDenied):
            CaseService.count_cases_by_lga(other_lga_id, mock_user_field_officer)
