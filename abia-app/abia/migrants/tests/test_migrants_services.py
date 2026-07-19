import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.migrants.services import MigrantService
from common.exceptions import MigrantNotFoundError, DuplicateMigrantError, InvalidPhoneError, LGAAccessDenied


class TestMigrantService:
    @patch("abia.migrants.services.MigrantRepository")
    def test_get_by_id(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock()
        result = MigrantService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(MigrantNotFoundError):
            MigrantService.get_by_id(uuid4())

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_as_admin(self, mock_repo):
        request = MagicMock()
        request.user.role = "state_admin"
        request.user.lga.id = uuid4()
        mock_repo.get_all.return_value = ["m1", "m2"]
        result = MigrantService.get_migrants_for_request(request)
        assert result == ["m1", "m2"]

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_as_officer(self, mock_repo):
        lga_id = uuid4()
        request = MagicMock()
        request.user.role = "field_officer"
        request.user.lga.id = lga_id
        mock_repo.get_by_lga.return_value = ["m1"]
        result = MigrantService.get_migrants_for_request(request)
        assert result == ["m1"]
        mock_repo.get_by_lga.assert_called_once_with(lga_id)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "full_name": "John Doe",
            "phone": "+2348012345678",
            "current_lga": MagicMock(id=lga_id),
        }
        mock_repo.get_by_lga.return_value = []
        mock_repo.create.return_value = MagicMock()
        result = MigrantService.create_migrant(data, officer)
        assert result is not None

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_invalid_phone(self, mock_repo):
        officer = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        data = {
            "full_name": "John Doe",
            "phone": "invalid-phone",
            "current_lga": MagicMock(id=uuid4()),
        }
        with pytest.raises(InvalidPhoneError):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_duplicate_phone(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "full_name": "John Doe",
            "phone": "+2348012345678",
            "current_lga": MagicMock(id=lga_id),
        }
        existing = MagicMock(phone="+2348012345678")
        mock_repo.get_by_lga.return_value = [existing]
        with pytest.raises(DuplicateMigrantError):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "full_name": "John Doe",
            "phone": "+2348012345678",
            "current_lga": MagicMock(id=lga_id),
        }
        mock_repo.get_by_lga.return_value = []
        mock_repo.create.return_value = MagicMock()
        result = MigrantService.create_migrant(data, officer)
        assert result is not None

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {
            "full_name": "John Doe",
            "phone": "+2348012345678",
            "current_lga": MagicMock(id=uuid4()),
        }
        with pytest.raises(LGAAccessDenied):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=MagicMock(id=lga_id))
        mock_repo.update.return_value = MagicMock()
        result = MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)
        assert result is not None

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_not_found(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = None
        with pytest.raises(MigrantNotFoundError):
            MigrantService.update_migrant(uuid4(), {}, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)


    @patch("abia.migrants.services.MigrantRepository")
    def test_delete_migrant_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(MigrantNotFoundError):
            MigrantService.delete_migrant(uuid4(), officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_delete_migrant_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(current_lga=MagicMock(id=lga_id))
        mock_repo.delete.return_value = True
        result = MigrantService.delete_migrant(uuid4(), officer)
        assert result is True

    @patch("abia.migrants.services.MigrantRepository")
    def test_delete_migrant_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(current_lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            MigrantService.delete_migrant(uuid4(), officer)
