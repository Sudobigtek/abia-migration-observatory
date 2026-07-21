
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import date
from abia.migrants.services import MigrantService
from common.exceptions import MigrantNotFoundError, DuplicateMigrantError, InvalidPhoneError, LGAAccessDenied


class TestMigrantServiceGet:
    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrant_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(full_name="John")
        result = MigrantService.get_by_id(uuid4())
        assert result.full_name == "John"

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrant_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(MigrantNotFoundError):
            MigrantService.get_by_id(uuid4())

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = MigrantService.get_migrants_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = MigrantService.get_migrants_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestMigrantServiceCreate:
    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_field_officer_same_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = []
        mock_repo.create.return_value = MagicMock(full_name="Jane")
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        result = MigrantService.create_migrant(data, officer)
        assert result.full_name == "Jane"

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_field_officer_other_lga_denied(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": other_lga,
        }
        with pytest.raises(LGAAccessDenied):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_duplicate_phone(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock(phone="+2348012345678")]
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        with pytest.raises(DuplicateMigrantError):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_invalid_phone(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = []
        data = {
            "full_name": "Jane",
            "phone": "invalid",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        with pytest.raises(InvalidPhoneError):
            MigrantService.create_migrant(data, officer)


class TestMigrantServiceUpdate:
    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(full_name="New")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)
        assert result.full_name == "New"

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(MigrantNotFoundError):
            MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_field_officer_other_lga_denied(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)
