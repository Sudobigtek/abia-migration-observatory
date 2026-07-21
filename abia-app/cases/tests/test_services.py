
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.cases.services import CaseService
from common.exceptions import CaseNotFoundError, InvalidStatusTransitionError, InvalidPriorityError, LGAAccessDenied


class TestCaseServiceGet:
    @patch("abia.cases.services.CaseRepository")
    def test_get_case_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(description="Test")
        result = CaseService.get_by_id(uuid4())
        assert result.description == "Test"

    @patch("abia.cases.services.CaseRepository")
    def test_get_case_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CaseNotFoundError):
            CaseService.get_by_id(uuid4())

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = CaseService.get_cases_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = CaseService.get_cases_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestCaseServiceCreate:
    @patch("abia.cases.services.CaseRepository")
    def test_create_case_field_officer_same_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.create.return_value = MagicMock(priority="high")
        data = {
            "migrant": MagicMock(),
            "lga": officer.lga,
            "priority": "high",
            "case_type": "medical",
            "description": "New case",
        }
        result = CaseService.create_case(data, officer)
        assert result.priority == "high"

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_field_officer_other_lga_denied(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        data = {
            "migrant": MagicMock(),
            "lga": other_lga,
            "priority": "high",
            "case_type": "medical",
            "description": "New case",
        }
        with pytest.raises(LGAAccessDenied):
            CaseService.create_case(data, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_invalid_priority(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {
            "migrant": MagicMock(),
            "lga": officer.lga,
            "priority": "invalid",
            "case_type": "medical",
            "description": "New case",
        }
        with pytest.raises(InvalidPriorityError):
            CaseService.create_case(data, officer)


class TestCaseServiceStatusTransitions:
    @patch("abia.cases.services.CaseRepository")
    def test_valid_transition_open_to_in_progress(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(status="in_progress")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = CaseService.update_status(uuid4(), "in_progress", officer)
        assert result.status == "in_progress"

    @patch("abia.cases.services.CaseRepository")
    def test_invalid_transition_open_to_resolved(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=uuid4()))
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidStatusTransitionError):
            CaseService.update_status(uuid4(), "resolved", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_field_officer_cannot_update_other_lga_case(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            CaseService.update_status(uuid4(), "in_progress", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_state_admin_can_update_any_case(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=other_lga)
        mock_repo.update.return_value = MagicMock(status="in_progress")
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        result = CaseService.update_status(uuid4(), "in_progress", admin)
        assert result.status == "in_progress"
