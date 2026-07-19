import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.accounts.services import LGAService, UserService
from common.exceptions import LGANotFoundError, LGAAccessDenied, UserNotFoundError, InvalidRoleError


class TestLGAService:
    @patch("abia.accounts.services.LGARepository")
    def test_get_all(self, mock_repo):
        mock_repo.get_all.return_value = ["lga1", "lga2"]
        result = LGAService.get_all()
        assert result == ["lga1", "lga2"]
        mock_repo.get_all.assert_called_once()

    @patch("abia.accounts.services.LGARepository")
    def test_get_by_id(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock()
        result = LGAService.get_by_id(uuid4())
        assert result is not None
        mock_repo.get_by_id.assert_called_once()

    @patch("abia.accounts.services.LGARepository")
    def test_get_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_id(uuid4())

    @patch("abia.accounts.services.LGARepository")
    def test_get_by_code(self, mock_repo):
        mock_repo.get_by_code.return_value = MagicMock()
        result = LGAService.get_by_code("ABN")
        assert result is not None

    @patch("abia.accounts.services.LGARepository")
    def test_get_by_code_not_found(self, mock_repo):
        mock_repo.get_by_code.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_code("NONEXISTENT")


class TestUserService:
    @patch("abia.accounts.services.UserRepository")
    def test_get_by_id(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock()
        result = UserService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_get_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            UserService.get_by_id(uuid4())

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_valid(self, mock_repo):
        creator = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        data = {"username": "newuser", "role": "field_officer", "lga": MagicMock(id=uuid4())}
        mock_repo.create.return_value = MagicMock()
        result = UserService.create(data, creator)
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_invalid_role(self, mock_repo):
        creator = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        data = {"username": "newuser", "role": "invalid_role", "lga": MagicMock(id=uuid4())}
        with pytest.raises(InvalidRoleError):
            UserService.create(data, creator)

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_field_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        creator = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {"username": "newuser", "role": "field_officer", "lga": MagicMock(id=lga_id)}
        mock_repo.create.return_value = MagicMock()
        result = UserService.create(data, creator)
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_field_officer_different_lga(self, mock_repo):
        creator = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {"username": "newuser", "role": "field_officer", "lga": MagicMock(id=uuid4())}
        with pytest.raises(LGAAccessDenied):
            UserService.create(data, creator)

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_as_admin(self, mock_repo):
        request = MagicMock()
        request.user.role = "state_admin"
        request.user.lga.id = uuid4()
        mock_repo.get_all.return_value = ["user1", "user2"]
        result = UserService.get_users_for_request(request)
        assert result == ["user1", "user2"]
        mock_repo.get_all.assert_called_once()

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_as_officer(self, mock_repo):
        lga_id = uuid4()
        request = MagicMock()
        request.user.role = "field_officer"
        request.user.lga.id = lga_id
        mock_repo.get_by_lga.return_value = ["user1"]
        result = UserService.get_users_for_request(request)
        assert result == ["user1"]
        mock_repo.get_by_lga.assert_called_once_with(lga_id)


    @patch("abia.accounts.services.UserRepository")
    def test_update_user_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        updater = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        with pytest.raises(UserNotFoundError):
            UserService.update(uuid4(), {}, updater)

    @patch("abia.accounts.services.UserRepository")
    def test_update_user_officer_different_lga(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock()
        updater = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            UserService.update(uuid4(), {}, updater)

    @patch("abia.accounts.services.UserRepository")
    def test_delete_user_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        deleter = MagicMock(role="super_admin", lga=MagicMock(id=uuid4()))
        with pytest.raises(UserNotFoundError):
            UserService.delete(uuid4(), deleter)

    @patch("abia.accounts.services.UserRepository")
    def test_delete_user_officer_different_lga(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(lga=MagicMock(id=uuid4()))
        deleter = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            UserService.delete(uuid4(), deleter)
