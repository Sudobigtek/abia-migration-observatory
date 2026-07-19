"""Unit tests for abia.referrals.services module.

Tests use mocked repositories (abia.referrals.repositories).
Matches actual repository methods: create, get_all, get_by_case, get_by_id, get_by_lga, update

Per Architecture Contract §8.1: Unit tests = 80% of pyramid.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from abia.referrals.repositories import ReferralRepository
from abia.referrals.services import ReferralService
from common.exceptions import (
    InvalidReferralStatusError,
    LGAAccessDenied,
    ReferralNotFoundError,
    SelfReferralError,
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
def mock_user_lga_coordinator():
    user = MagicMock()
    user.id = uuid4()
    user.role = "lga_coordinator"
    user.lga_id = uuid4()
    user.lga = MagicMock()
    user.lga.name = "Aba South"
    return user


@pytest.fixture
def mock_user_state_admin():
    user = MagicMock()
    user.id = uuid4()
    user.role = "state_admin"
    user.lga_id = uuid4()
    return user


@pytest.fixture
def mock_referral(mock_user_field_officer, mock_user_lga_coordinator):
    referral = MagicMock()
    referral.id = uuid4()
    referral.case_id = uuid4()
    referral.migrant_id = uuid4()
    referral.from_lga_id = mock_user_field_officer.lga_id
    referral.to_lga_id = mock_user_lga_coordinator.lga_id
    referral.to_organization = "Specialist Hospital"
    referral.to_contact_name = "Dr. Smith"
    referral.to_contact_phone = "+2348099999999"
    referral.status = "pending"
    referral.reason = "Medical emergency requiring specialist care"
    referral.camunda_process_id = None
    referral.created_at = datetime(2026, 7, 1, 10, 0, 0)
    referral.updated_at = datetime(2026, 7, 1, 10, 0, 0)
    referral.created_by_id = mock_user_field_officer.id
    return referral


@pytest.fixture
def valid_referral_data(mock_user_field_officer, mock_user_lga_coordinator):
    return {
        "case_id": str(uuid4()),
        "from_lga_id": str(mock_user_field_officer.lga_id),
        "to_lga_id": str(mock_user_lga_coordinator.lga_id),
        "to_organization": "Specialist Hospital",
        "to_contact_name": "Dr. Smith",
        "to_contact_phone": "+2348099999999",
        "reason": "Medical emergency requiring specialist care",
        "status": "pending",
    }


class TestReferralServiceListRetrieve:
    def test_get_referrals_for_request_field_officer(
        self, mock_user_field_officer, mock_referral
    ):
        with patch.object(
            ReferralRepository, "get_by_lga", return_value=[mock_referral]
        ) as mock_repo:
            result = ReferralService.get_referrals_for_request(mock_user_field_officer)
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
            assert result[0].reason == "Medical emergency requiring specialist care"

    def test_get_referrals_for_request_state_admin(
        self, mock_user_state_admin, mock_referral
    ):
        with patch.object(
            ReferralRepository, "get_all", return_value=[mock_referral]
        ) as mock_repo:
            result = ReferralService.get_referrals_for_request(mock_user_state_admin)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_referral_by_id_found_same_lga(
        self, mock_user_field_officer, mock_referral
    ):
        with patch.object(
            ReferralRepository, "get_by_id", return_value=mock_referral
        ) as mock_repo:
            result = ReferralService.get_referral_by_id(
                mock_referral.id, mock_user_field_officer
            )
            mock_repo.assert_called_once_with(mock_referral.id)
            assert result == mock_referral

    def test_get_referral_by_id_not_found(self, mock_user_field_officer):
        referral_id = uuid4()
        with patch.object(
            ReferralRepository, "get_by_id", return_value=None
        ) as mock_repo:
            with pytest.raises(ReferralNotFoundError):
                ReferralService.get_referral_by_id(referral_id, mock_user_field_officer)
            mock_repo.assert_called_once_with(referral_id)

    def test_get_referral_by_id_field_officer_other_lga(self, mock_user_field_officer):
        other_referral = MagicMock()
        other_referral.id = uuid4()
        other_referral.from_lga_id = uuid4()
        other_referral.to_lga_id = uuid4()
        with patch.object(ReferralRepository, "get_by_id", return_value=other_referral):
            with pytest.raises(LGAAccessDenied):
                ReferralService.get_referral_by_id(
                    other_referral.id, mock_user_field_officer
                )

    def test_get_referral_by_id_state_admin_other_lga(self, mock_user_state_admin):
        other_referral = MagicMock()
        other_referral.id = uuid4()
        other_referral.from_lga_id = uuid4()
        other_referral.to_lga_id = uuid4()
        with patch.object(
            ReferralRepository, "get_by_id", return_value=other_referral
        ) as mock_repo:
            result = ReferralService.get_referral_by_id(
                other_referral.id, mock_user_state_admin
            )
            mock_repo.assert_called_once_with(other_referral.id)
            assert result == other_referral


class TestReferralServiceCreate:
    def test_create_referral_field_officer_same_lga(
        self, mock_user_field_officer, valid_referral_data
    ):
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.from_lga_id = mock_user_field_officer.lga_id
        mock_created.status = "pending"
        with patch.object(
            ReferralRepository, "create", return_value=mock_created
        ) as mock_create:
            result = ReferralService.create_referral(
                valid_referral_data, mock_user_field_officer
            )
            mock_create.assert_called_once()
            assert result.status == "pending"

    def test_create_referral_field_officer_different_from_lga(
        self, mock_user_field_officer, valid_referral_data
    ):
        valid_referral_data["from_lga_id"] = str(uuid4())
        with pytest.raises(LGAAccessDenied) as exc_info:
            ReferralService.create_referral(
                valid_referral_data, mock_user_field_officer
            )
        assert (
            "outside your LGA" in str(exc_info.value).lower()
            or "from_lga" in str(exc_info.value).lower()
        )

    def test_create_referral_self_referral(
        self, mock_user_field_officer, valid_referral_data
    ):
        valid_referral_data["to_lga_id"] = valid_referral_data["from_lga_id"]
        with pytest.raises(SelfReferralError) as exc_info:
            ReferralService.create_referral(
                valid_referral_data, mock_user_field_officer
            )
        assert (
            "same LGA" in str(exc_info.value).lower()
            or "self" in str(exc_info.value).lower()
        )

    def test_create_referral_state_admin_any_lga(
        self, mock_user_state_admin, valid_referral_data
    ):
        valid_referral_data["from_lga_id"] = str(uuid4())
        mock_created = MagicMock()
        mock_created.id = uuid4()
        with patch.object(
            ReferralRepository, "create", return_value=mock_created
        ) as mock_create:
            result = ReferralService.create_referral(
                valid_referral_data, mock_user_state_admin
            )
            mock_create.assert_called_once()
            assert result is not None

    def test_create_referral_missing_reason(
        self, mock_user_field_officer, valid_referral_data
    ):
        invalid_data = valid_referral_data.copy()
        invalid_data["reason"] = ""
        with pytest.raises(ValidationError) as exc_info:
            ReferralService.create_referral(invalid_data, mock_user_field_officer)
        assert "reason" in str(exc_info.value).lower()

    def test_create_referral_missing_case_id(
        self, mock_user_field_officer, valid_referral_data
    ):
        invalid_data = valid_referral_data.copy()
        invalid_data["case_id"] = ""
        with pytest.raises(ValidationError) as exc_info:
            ReferralService.create_referral(invalid_data, mock_user_field_officer)
        assert "case" in str(exc_info.value).lower()

    def test_create_referral_invalid_status(
        self, mock_user_field_officer, valid_referral_data
    ):
        invalid_data = valid_referral_data.copy()
        invalid_data["status"] = "accepted"
        with pytest.raises((ValidationError, InvalidReferralStatusError)) as exc_info:
            ReferralService.create_referral(invalid_data, mock_user_field_officer)
        assert "status" in str(exc_info.value).lower()


class TestReferralServiceUpdate:
    def test_update_referral_field_officer_same_lga(
        self, mock_user_field_officer, mock_referral
    ):
        update_data = {"reason": "Updated reason"}
        updated_referral = MagicMock()
        updated_referral.reason = "Updated reason"
        updated_referral.from_lga_id = mock_user_field_officer.lga_id
        with patch.object(
            ReferralRepository, "get_by_id", return_value=mock_referral
        ), patch.object(
            ReferralRepository, "update", return_value=updated_referral
        ) as mock_update:
            result = ReferralService.update_referral(
                mock_referral.id, update_data, mock_user_field_officer
            )
            mock_update.assert_called_once()
            assert result.reason == "Updated reason"

    def test_update_referral_field_officer_other_lga(self, mock_user_field_officer):
        other_referral = MagicMock()
        other_referral.id = uuid4()
        other_referral.from_lga_id = uuid4()
        update_data = {"reason": "Updated"}
        with patch.object(ReferralRepository, "get_by_id", return_value=other_referral):
            with pytest.raises(LGAAccessDenied):
                ReferralService.update_referral(
                    other_referral.id, update_data, mock_user_field_officer
                )

    def test_update_referral_not_found(self, mock_user_field_officer):
        referral_id = uuid4()
        update_data = {"reason": "Updated"}
        with patch.object(ReferralRepository, "get_by_id", return_value=None):
            with pytest.raises(ReferralNotFoundError):
                ReferralService.update_referral(
                    referral_id, update_data, mock_user_field_officer
                )

    def test_update_referral_status_transition_valid(
        self, mock_user_field_officer, mock_referral
    ):
        update_data = {"status": "in_progress"}
        updated_referral = MagicMock()
        updated_referral.status = "in_progress"
        updated_referral.from_lga_id = mock_user_field_officer.lga_id
        with patch.object(
            ReferralRepository, "get_by_id", return_value=mock_referral
        ), patch.object(
            ReferralRepository, "update", return_value=updated_referral
        ) as mock_update:
            result = ReferralService.update_referral(
                mock_referral.id, update_data, mock_user_field_officer
            )
            mock_update.assert_called_once()
            assert result.status == "in_progress"

    def test_update_referral_status_transition_invalid(
        self, mock_user_field_officer, mock_referral
    ):
        update_data = {"status": "completed"}
        with patch.object(ReferralRepository, "get_by_id", return_value=mock_referral):
            with pytest.raises(InvalidReferralStatusError) as exc_info:
                ReferralService.update_referral(
                    mock_referral.id, update_data, mock_user_field_officer
                )
            assert (
                "status" in str(exc_info.value).lower()
                or "transition" in str(exc_info.value).lower()
            )


class TestReferralServiceCount:
    def test_count_referrals_by_lga_field_officer(self, mock_user_field_officer):
        with patch.object(
            ReferralRepository, "get_by_lga", return_value=[MagicMock(), MagicMock()]
        ) as mock_repo:
            result = ReferralService.count_referrals_by_lga(
                mock_user_field_officer.lga_id, mock_user_field_officer
            )
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert result == 2

    def test_count_referrals_by_lga_field_officer_other_lga(
        self, mock_user_field_officer
    ):
        other_lga_id = uuid4()
        with pytest.raises(LGAAccessDenied):
            ReferralService.count_referrals_by_lga(
                other_lga_id, mock_user_field_officer
            )
