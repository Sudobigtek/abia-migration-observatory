import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.cases.services import CaseService
from common.exceptions import CaseNotFoundError, InvalidStatusTransitionError, InvalidPriorityError, LGAAccessDenied


class TestCaseService:
    @patch("abia.cases.services.CaseRepository")
    def test_get_by_id(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock()
        result = CaseService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.cases.services.CaseRepository")
    def test_get_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CaseNotFoundError):
            CaseService.get_by_id(uuid4())

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_as_admin(self, mock_repo):
        request = MagicMock()
        request.user.role = "state_admin"
        request.user.lga.id = uuid4()
        mock_repo.get_all.return_value = ["c1", "c2"]
        result = CaseService.get_cases_for_request(request)
        assert result == ["c1", "c2"]

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_as_officer(self, mock_repo):
        lga_id = uuid4()
        request = MagicMock()
        request.user.role = "field_officer"
        request.user.lga.id = lga_id
        mock_repo.get_by_lga.return_value = ["c1"]
        result = CaseService.get_cases_for_request(request)
        assert result == ["c1"]
        mock_repo.get_by_lga.assert_called_once_with(lga_id)

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "migrant": MagicMock(id=uuid4()),
            "lga": MagicMock(id=lga_id),
            "status": "open",
            "priority": "medium",
        }
        mock_repo.create.return_value = MagicMock()
        result = CaseService.create_case(data, officer)
        assert result is not None

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_invalid_priority(self, mock_repo):
        officer = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        data = {
            "migrant": MagicMock(id=uuid4()),
            "lga": MagicMock(id=uuid4()),
            "status": "open",
            "priority": "invalid",
        }
        with pytest.raises(InvalidPriorityError):
            CaseService.create_case(data, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "migrant": MagicMock(id=uuid4()),
            "lga": MagicMock(id=lga_id),
            "status": "open",
            "priority": "medium",
        }
        mock_repo.create.return_value = MagicMock()
        result = CaseService.create_case(data, officer)
        assert result is not None

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {
            "migrant": MagicMock(id=uuid4()),
            "lga": MagicMock(id=uuid4()),
            "status": "open",
            "priority": "medium",
        }
        with pytest.raises(LGAAccessDenied):
            CaseService.create_case(data, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_update_status_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=lga_id))
        mock_repo.update.return_value = MagicMock()
        result = CaseService.update_status(uuid4(), "in_progress", officer)
        assert result is not None

    @patch("abia.cases.services.CaseRepository")
    def test_update_status_invalid_transition(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=lga_id))
        with pytest.raises(InvalidStatusTransitionError):
            CaseService.update_status(uuid4(), "resolved", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_update_status_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            CaseService.update_status(uuid4(), "in_progress", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_update_status_not_found(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CaseNotFoundError):
            CaseService.update_status(uuid4(), "in_progress", officer)


    @patch("abia.cases.services.CaseRepository")
    def test_update_case_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(CaseNotFoundError):
            CaseService.update_case(uuid4(), {}, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_update_case_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            CaseService.update_case(uuid4(), {}, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_delete_case_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(CaseNotFoundError):
            CaseService.delete_case(uuid4(), officer)

    @patch("abia.cases.services.CaseRepository")
    def test_delete_case_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(lga=MagicMock(id=lga_id))
        mock_repo.delete.return_value = True
        result = CaseService.delete_case(uuid4(), officer)
        assert result is True

    @patch("abia.cases.services.CaseRepository")
    def test_delete_case_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            CaseService.delete_case(uuid4(), officer)
