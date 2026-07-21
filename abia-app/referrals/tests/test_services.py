
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.referrals.services import ReferralService
from common.exceptions import ReferralNotFoundError, InvalidReferralStatusError, SelfReferralError, LGAAccessDenied


class TestReferralServiceGet:
    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referral_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(reason="Medical")
        result = ReferralService.get_by_id(uuid4())
        assert result.reason == "Medical"

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referral_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ReferralNotFoundError):
            ReferralService.get_by_id(uuid4())

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = ReferralService.get_referrals_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = ReferralService.get_referrals_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestReferralServiceCreate:
    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_valid(self, mock_repo):
        from_lga = MagicMock(id=uuid4())
        to_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=from_lga)
        mock_repo.create.return_value = MagicMock(status="pending")
        data = {
            "case": MagicMock(),
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        result = ReferralService.create_referral(data, officer)
        assert result.status == "pending"

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_self_referral(self, mock_repo):
        same_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=same_lga)
        data = {
            "case": MagicMock(),
            "from_lga": same_lga,
            "to_lga": same_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        with pytest.raises(SelfReferralError):
            ReferralService.create_referral(data, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_field_officer_from_other_lga_denied(self, mock_repo):
        officer_lga = MagicMock(id=uuid4())
        from_lga = MagicMock(id=uuid4())
        to_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=officer_lga)
        data = {
            "case": MagicMock(),
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        with pytest.raises(LGAAccessDenied):
            ReferralService.create_referral(data, officer)


class TestReferralServiceStatusTransitions:
    @patch("abia.referrals.services.ReferralRepository")
    def test_accept_pending_referral(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(status="accepted")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = ReferralService.update_status(uuid4(), "accepted", officer)
        assert result.status == "accepted"

    @patch("abia.referrals.services.ReferralRepository")
    def test_invalid_transition_pending_to_completed(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=MagicMock(id=uuid4()))
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidReferralStatusError):
            ReferralService.update_status(uuid4(), "completed", officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_field_officer_cannot_update_other_lga_referral(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            ReferralService.update_status(uuid4(), "accepted", officer)
