
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.accounts.services import LGAService, UserService
from common.exceptions import LGANotFoundError, LGAAccessDenied, UserNotFoundError, InvalidRoleError


class TestLGAService:
    @patch("abia.accounts.services.LGARepository")
    def test_get_all_lgas(self, mock_repo):
        mock_repo.get_all.return_value = [MagicMock(name="Aba North")]
        result = LGAService.get_all()
        assert len(result) == 1

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(name="Aba North")
        result = LGAService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_id(uuid4())

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_code_found(self, mock_repo):
        mock_repo.get_by_code.return_value = MagicMock(name="Aba North")
        result = LGAService.get_by_code("ABN")
        assert result is not None

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_code_not_found(self, mock_repo):
        mock_repo.get_by_code.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_code("XXX")


class TestUserService:
    @patch("abia.accounts.services.UserRepository")
    def test_get_user_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(username="test")
        result = UserService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_get_user_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            UserService.get_by_id(uuid4())

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_valid_role(self, mock_repo):
        mock_user = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.create.return_value = mock_user
        result = UserService.create({"role": "field_officer", "lga": mock_user.lga}, mock_user)
        assert result.role == "field_officer"

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_invalid_role(self, mock_repo):
        mock_user = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidRoleError):
            UserService.create({"role": "invalid_role", "lga": mock_user.lga}, mock_user)

    @patch("abia.accounts.services.UserRepository")
    def test_field_officer_cannot_create_outside_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        with pytest.raises(LGAAccessDenied):
            UserService.create({"role": "field_officer", "lga": other_lga}, officer)

    @patch("abia.accounts.services.UserRepository")
    def test_state_admin_can_create_any_lga(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        mock_repo.create.return_value = MagicMock(role="field_officer")
        result = UserService.create({"role": "field_officer", "lga": other_lga}, admin)
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = UserService.get_users_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = UserService.get_users_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()
