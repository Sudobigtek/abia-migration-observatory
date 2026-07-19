"""Unit tests for abia.migrants.services module.

Tests use mocked repositories (abia.migrants.repositories).
Matches actual repository methods: create, get_all, get_by_id, get_by_lga, update

Per Architecture Contract §8.1: Unit tests = 80% of pyramid.
"""

from datetime import date
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from abia.migrants.repositories import MigrantRepository
from abia.migrants.services import MigrantService
from common.exceptions import (
    LGAAccessDenied,
    LGANotFoundError,
    MigrantNotFoundError,
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
def mock_migrant(mock_user_field_officer):
    migrant = MagicMock()
    migrant.id = uuid4()
    migrant.full_name = "John Doe"
    migrant.phone = "+2348012345678"
    migrant.date_of_birth = date(1990, 5, 15)
    migrant.current_lga_id = mock_user_field_officer.lga_id
    migrant.lga_of_origin_id = uuid4()
    migrant.status = "active"
    migrant.created_at = "2026-07-01T10:00:00Z"
    return migrant


@pytest.fixture
def valid_migrant_data(mock_user_field_officer):
    return {
        "full_name": "Jane Smith",
        "phone": "+2348098765432",
        "date_of_birth": date(1985, 3, 20),
        "current_lga_id": str(mock_user_field_officer.lga_id),
        "lga_of_origin_id": str(uuid4()),
        "status": "active",
    }


class TestMigrantServiceListRetrieve:
    def test_get_migrants_for_request_field_officer(
        self, mock_user_field_officer, mock_migrant
    ):
        with patch.object(
            MigrantRepository, "get_by_lga", return_value=[mock_migrant]
        ) as mock_repo:
            result = MigrantService.get_migrants_for_request(mock_user_field_officer)
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert len(result) == 1
            assert result[0].full_name == "John Doe"

    def test_get_migrants_for_request_state_admin(
        self, mock_user_state_admin, mock_migrant
    ):
        with patch.object(
            MigrantRepository, "get_all", return_value=[mock_migrant]
        ) as mock_repo:
            result = MigrantService.get_migrants_for_request(mock_user_state_admin)
            mock_repo.assert_called_once()
            assert len(result) == 1

    def test_get_migrant_by_id_found_same_lga(
        self, mock_user_field_officer, mock_migrant
    ):
        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ) as mock_repo:
            result = MigrantService.get_migrant_by_id(
                mock_migrant.id, mock_user_field_officer
            )
            mock_repo.assert_called_once_with(mock_migrant.id)
            assert result == mock_migrant

    def test_get_migrant_by_id_not_found(self, mock_user_field_officer):
        migrant_id = uuid4()
        with patch.object(
            MigrantRepository, "get_by_id", return_value=None
        ) as mock_repo:
            with pytest.raises(MigrantNotFoundError):
                MigrantService.get_migrant_by_id(migrant_id, mock_user_field_officer)
            mock_repo.assert_called_once_with(migrant_id)

    def test_get_migrant_by_id_field_officer_other_lga(self, mock_user_field_officer):
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()
        with patch.object(MigrantRepository, "get_by_id", return_value=other_migrant):
            with pytest.raises(LGAAccessDenied):
                MigrantService.get_migrant_by_id(
                    other_migrant.id, mock_user_field_officer
                )

    def test_get_migrant_by_id_state_admin_other_lga(self, mock_user_state_admin):
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()
        with patch.object(
            MigrantRepository, "get_by_id", return_value=other_migrant
        ) as mock_repo:
            result = MigrantService.get_migrant_by_id(
                other_migrant.id, mock_user_state_admin
            )
            mock_repo.assert_called_once_with(other_migrant.id)
            assert result == other_migrant


class TestMigrantServiceCreate:
    def test_create_migrant_field_officer_same_lga(
        self, mock_user_field_officer, valid_migrant_data
    ):
        mock_created = MagicMock()
        mock_created.id = uuid4()
        mock_created.full_name = valid_migrant_data["full_name"]
        with patch.object(
            MigrantRepository, "create", return_value=mock_created
        ) as mock_create:
            result = MigrantService.create_migrant(
                valid_migrant_data, mock_user_field_officer
            )
            mock_create.assert_called_once()
            assert result.full_name == "Jane Smith"

    def test_create_migrant_field_officer_different_lga(
        self, mock_user_field_officer, valid_migrant_data
    ):
        valid_migrant_data["current_lga_id"] = str(uuid4())
        with pytest.raises(LGAAccessDenied) as exc_info:
            MigrantService.create_migrant(valid_migrant_data, mock_user_field_officer)
        assert "outside your LGA" in str(exc_info.value).lower()

    def test_create_migrant_state_admin_any_lga(
        self, mock_user_state_admin, valid_migrant_data
    ):
        valid_migrant_data["current_lga_id"] = str(uuid4())
        mock_created = MagicMock()
        mock_created.id = uuid4()
        with patch.object(
            MigrantRepository, "create", return_value=mock_created
        ) as mock_create:
            result = MigrantService.create_migrant(
                valid_migrant_data, mock_user_state_admin
            )
            mock_create.assert_called_once()
            assert result is not None

    def test_create_migrant_missing_full_name(
        self, mock_user_field_officer, valid_migrant_data
    ):
        invalid_data = valid_migrant_data.copy()
        invalid_data["full_name"] = ""
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)
        assert "full_name" in str(exc_info.value).lower()

    def test_create_migrant_missing_phone(
        self, mock_user_field_officer, valid_migrant_data
    ):
        invalid_data = valid_migrant_data.copy()
        invalid_data["phone"] = ""
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)
        assert "phone" in str(exc_info.value).lower()

    def test_create_migrant_invalid_phone_format(
        self, mock_user_field_officer, valid_migrant_data
    ):
        invalid_data = valid_migrant_data.copy()
        invalid_data["phone"] = "12345"
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)
        assert "phone" in str(exc_info.value).lower()

    def test_create_migrant_future_date_of_birth(
        self, mock_user_field_officer, valid_migrant_data
    ):
        from datetime import datetime, timedelta

        invalid_data = valid_migrant_data.copy()
        invalid_data["date_of_birth"] = datetime.now().date() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            MigrantService.create_migrant(invalid_data, mock_user_field_officer)
        assert (
            "date" in str(exc_info.value).lower()
            or "future" in str(exc_info.value).lower()
        )


class TestMigrantServiceUpdate:
    def test_update_migrant_field_officer_same_lga(
        self, mock_user_field_officer, mock_migrant
    ):
        update_data = {"full_name": "Updated Name"}
        updated_migrant = MagicMock()
        updated_migrant.full_name = "Updated Name"
        updated_migrant.current_lga_id = mock_user_field_officer.lga_id
        with patch.object(
            MigrantRepository, "get_by_id", return_value=mock_migrant
        ), patch.object(
            MigrantRepository, "update", return_value=updated_migrant
        ) as mock_update:
            result = MigrantService.update_migrant(
                mock_migrant.id, update_data, mock_user_field_officer
            )
            mock_update.assert_called_once()
            assert result.full_name == "Updated Name"

    def test_update_migrant_field_officer_other_lga(self, mock_user_field_officer):
        other_migrant = MagicMock()
        other_migrant.id = uuid4()
        other_migrant.current_lga_id = uuid4()
        update_data = {"full_name": "Updated Name"}
        with patch.object(MigrantRepository, "get_by_id", return_value=other_migrant):
            with pytest.raises(LGAAccessDenied):
                MigrantService.update_migrant(
                    other_migrant.id, update_data, mock_user_field_officer
                )

    def test_update_migrant_not_found(self, mock_user_field_officer):
        migrant_id = uuid4()
        update_data = {"full_name": "Updated Name"}
        with patch.object(MigrantRepository, "get_by_id", return_value=None):
            with pytest.raises(MigrantNotFoundError):
                MigrantService.update_migrant(
                    migrant_id, update_data, mock_user_field_officer
                )


class TestMigrantServiceCount:
    def test_count_migrants_by_lga_field_officer(self, mock_user_field_officer):
        with patch.object(
            MigrantRepository, "get_by_lga", return_value=[MagicMock(), MagicMock()]
        ) as mock_repo:
            result = MigrantService.count_migrants_by_lga(
                mock_user_field_officer.lga_id, mock_user_field_officer
            )
            mock_repo.assert_called_once_with(mock_user_field_officer.lga_id)
            assert result == 2

    def test_count_migrants_by_lga_field_officer_other_lga(
        self, mock_user_field_officer
    ):
        other_lga_id = uuid4()
        with pytest.raises(LGAAccessDenied):
            MigrantService.count_migrants_by_lga(other_lga_id, mock_user_field_officer)
