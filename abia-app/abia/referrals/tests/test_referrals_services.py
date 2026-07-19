import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.referrals.services import ReferralService
from common.exceptions import ReferralNotFoundError, InvalidReferralStatusError, SelfReferralError, LGAAccessDenied


class TestReferralService:
    @patch("abia.referrals.services.ReferralRepository")
    def test_get_by_id(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock()
        result = ReferralService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ReferralNotFoundError):
            ReferralService.get_by_id(uuid4())

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_as_admin(self, mock_repo):
        request = MagicMock()
        request.user.role = "state_admin"
        request.user.lga.id = uuid4()
        mock_repo.get_all.return_value = ["r1", "r2"]
        result = ReferralService.get_referrals_for_request(request)
        assert result == ["r1", "r2"]

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_as_officer(self, mock_repo):
        lga_id = uuid4()
        request = MagicMock()
        request.user.role = "field_officer"
        request.user.lga.id = lga_id
        mock_repo.get_by_lga.return_value = ["r1"]
        result = ReferralService.get_referrals_for_request(request)
        assert result == ["r1"]
        mock_repo.get_by_lga.assert_called_once_with(lga_id)

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "case": MagicMock(id=uuid4()),
            "from_lga": MagicMock(id=lga_id),
            "to_lga": MagicMock(id=uuid4()),
            "status": "pending",
        }
        mock_repo.create.return_value = MagicMock()
        result = ReferralService.create_referral(data, officer)
        assert result is not None

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_self(self, mock_repo):
        lga_id = uuid4()
        same_lga = MagicMock(id=lga_id)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "case": MagicMock(id=uuid4()),
            "from_lga": same_lga,
            "to_lga": same_lga,
            "status": "pending",
        }
        with pytest.raises(SelfReferralError):
            ReferralService.create_referral(data, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        data = {
            "case": MagicMock(id=uuid4()),
            "from_lga": MagicMock(id=lga_id),
            "to_lga": MagicMock(id=uuid4()),
            "status": "pending",
        }
        mock_repo.create.return_value = MagicMock()
        result = ReferralService.create_referral(data, officer)
        assert result is not None

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {
            "case": MagicMock(id=uuid4()),
            "from_lga": MagicMock(id=uuid4()),
            "to_lga": MagicMock(id=uuid4()),
            "status": "pending",
        }
        with pytest.raises(LGAAccessDenied):
            ReferralService.create_referral(data, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_update_status_valid(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(
            status="pending", from_lga=MagicMock(id=lga_id)
        )
        mock_repo.update.return_value = MagicMock()
        result = ReferralService.update_status(uuid4(), "accepted", officer)
        assert result is not None

    @patch("abia.referrals.services.ReferralRepository")
    def test_update_status_invalid_transition(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(
            status="pending", from_lga=MagicMock(id=lga_id)
        )
        with pytest.raises(InvalidReferralStatusError):
            ReferralService.update_status(uuid4(), "completed", officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_update_status_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(
            status="pending", from_lga=MagicMock(id=uuid4())
        )
        with pytest.raises(LGAAccessDenied):
            ReferralService.update_status(uuid4(), "accepted", officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_update_status_not_found(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ReferralNotFoundError):
            ReferralService.update_status(uuid4(), "accepted", officer)


    @patch("abia.referrals.services.ReferralRepository")
    def test_update_referral_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(ReferralNotFoundError):
            ReferralService.update_referral(uuid4(), {}, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_update_referral_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(from_lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            ReferralService.update_referral(uuid4(), {}, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_delete_referral_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(ReferralNotFoundError):
            ReferralService.delete_referral(uuid4(), officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_delete_referral_officer_same_lga(self, mock_repo):
        lga_id = uuid4()
        officer = MagicMock(role="field_officer", lga=MagicMock(id=lga_id))
        mock_repo.get_by_id.return_value = MagicMock(from_lga=MagicMock(id=lga_id))
        mock_repo.delete.return_value = True
        result = ReferralService.delete_referral(uuid4(), officer)
        assert result is True

    @patch("abia.referrals.services.ReferralRepository")
    def test_delete_referral_officer_different_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_id.return_value = MagicMock(from_lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            ReferralService.delete_referral(uuid4(), officer)
