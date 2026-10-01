"""Tests for ODK Bridge service layer."""

import pytest
from django.contrib.gis.geos import Point

from abia.common.exceptions import (
    LGANotFoundError,
    DuplicateSubmissionError,
    InvalidGPSDataError,
)
from abia.migrants.odk_bridge import ODKBridge
from abia.migrants.models import Migrant


@pytest.mark.django_db
class TestODKBridge:
    """Test ODK submission processing end-to-end."""

    def test_process_submission_success(self, test_user):
        """Given valid ODK data, create Migrant record."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()
        assert lga is not None, "LGA fixture required"

        data = {
            "meta": {"instanceID": "uuid:abc123"},
            "data": {
                "full_name": "John ODK",
                "phone": "+2348111111111",
                "gender": "male",
                "current_lga": lga.name,
                "gps": "5.123 7.456 0 0",
            }
        }

        migrant = ODKBridge.process_submission(data, test_user)

        assert isinstance(migrant, Migrant)
        assert migrant.full_name == "John ODK"
        assert migrant.odk_submission_id == "uuid:abc123"
        assert migrant.current_lga == lga
        assert migrant.gps_coordinates is not None

    def test_duplicate_submission_rejected(self, test_user):
        """Given same instanceID twice, raise DuplicateSubmissionError."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()

        data = {
            "meta": {"instanceID": "uuid:dup456"},
            "data": {
                "full_name": "First",
                "phone": "+2348111111111",
                "gender": "male",
                "current_lga": lga.name,
            }
        }

        ODKBridge.process_submission(data, test_user)

        with pytest.raises(DuplicateSubmissionError) as exc:
            ODKBridge.process_submission(data, test_user)
        assert "uuid:dup456" in str(exc.value)

    def test_missing_lga_raises_error(self, test_user):
        """Given non-existent LGA, raise LGANotFoundError."""
        data = {
            "meta": {"instanceID": "uuid:lga789"},
            "data": {
                "full_name": "No LGA",
                "current_lga": "NonExistentLGA12345",
            }
        }

        with pytest.raises(LGANotFoundError) as exc:
            ODKBridge.process_submission(data, test_user)
        assert "NonExistentLGA12345" in str(exc.value)

    def test_gps_parsing_success(self):
        """Given valid GPS string, return GeoDjango Point."""
        point = ODKBridge._parse_gps({"gps": "5.123 7.456 100 5"})
        assert isinstance(point, Point)
        assert point.x == 7.456
        assert point.y == 5.123
        assert point.srid == 4326

    def test_gps_parsing_missing(self):
        """Given no GPS, return None."""
        assert ODKBridge._parse_gps({}) is None

    def test_gps_parsing_invalid_raises(self):
        """Given malformed GPS, raise InvalidGPSDataError."""
        with pytest.raises(InvalidGPSDataError):
            ODKBridge._parse_gps({"gps": "not-a-coordinate"})

    def test_submission_id_extraction(self):
        """Extract instanceID from meta block."""
        assert ODKBridge._extract_submission_id(
            {"meta": {"instanceID": "uuid:test"}}
        ) == "uuid:test"

    def test_submission_id_fallback(self):
        """Fallback to __id if meta missing."""
        assert ODKBridge._extract_submission_id(
            {"__id": "fallback-id"}
        ) == "fallback-id"

    def test_submission_id_missing_raises(self):
        """Raise ValueError if no ID found."""
        with pytest.raises(ValueError):
            ODKBridge._extract_submission_id({})
