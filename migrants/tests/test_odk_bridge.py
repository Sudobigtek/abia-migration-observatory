"""Tests for ODK Bridge — Architecture Contract §8.1, §16.2."""

import pytest
from datetime import date
from django.contrib.gis.geos import Point

try:
    from common.exceptions import (
        DuplicateSubmissionError,
        LGANotFoundError,
        InvalidSubmissionError,
    )
except ImportError:
    from abia.common.exceptions import (
        DuplicateSubmissionError,
        LGANotFoundError,
        InvalidSubmissionError,
    )

try:
    from accounts.models import LGA
except ImportError:
    from abia.accounts.models import LGA

from migrants.models import Migrant
from migrants.odk_bridge import ODKBridge


@pytest.fixture
def valid_submission():
    return {
        "__system": {"instanceID": "uuid:abc-123"},
        "current_lga": "aba_north",
        "full_name": "John Doe",
        "gender": "male",
        "date_of_birth": "1990-05-15",
        "country_of_origin": "nigeria",
        "state_of_origin": "abia",
        "phone_number": "+2348012345678",
        "id_number": "12345678901",
        "migrant_status": "returnee",
        "services_needed": "medical legal",
        "household_size": "4",
        "vulnerable": "no",
        "enumerator_id": "NCF-001",
        "gps_coords": "5.123 7.456 0 0",
    }


@pytest.fixture
def lga_aba_north(db):
    return LGA.objects.create(name="Aba North", code="aba_north")


@pytest.fixture
def lga_aba_south(db):
    return LGA.objects.create(name="Aba South", code="aba_south")


@pytest.mark.django_db
class TestProcessSubmission:
    def test_creates_migrant_from_valid(self, lga_aba_north, valid_submission):
        m = ODKBridge.process_submission(valid_submission)
        assert isinstance(m, Migrant)
        assert m.full_name == "John Doe"
        assert m.current_lga == lga_aba_north
        assert m.gender == "male"
        assert m.date_of_birth == date(1990, 5, 15)
        assert m.phone_number == "+2348012345678"
        assert m.household_size == 4
        assert m.is_vulnerable is False
        assert m.odk_submission_id == "uuid:abc-123"

    def test_parses_gps_to_point(self, lga_aba_north, valid_submission):
        m = ODKBridge.process_submission(valid_submission)
        assert isinstance(m.location, Point)
        assert m.location.x == pytest.approx(7.456)
        assert m.location.y == pytest.approx(5.123)

    def test_duplicate_raises(self, lga_aba_north, valid_submission):
        ODKBridge.process_submission(valid_submission)
        with pytest.raises(DuplicateSubmissionError):
            ODKBridge.process_submission(valid_submission)

    def test_missing_lga_raises(self, valid_submission):
        valid_submission["current_lga"] = "nonexistent"
        with pytest.raises(LGANotFoundError):
            ODKBridge.process_submission(valid_submission)

    def test_missing_instance_id_raises(self, valid_submission):
        del valid_submission["__system"]
        with pytest.raises(InvalidSubmissionError):
            ODKBridge.process_submission(valid_submission)

    def test_missing_current_lga_raises(self, lga_aba_north, valid_submission):
        del valid_submission["current_lga"]
        with pytest.raises(InvalidSubmissionError):
            ODKBridge.process_submission(valid_submission)


@pytest.mark.django_db
class TestProcessBulk:
    def test_bulk_mixed_results(self, lga_aba_north, valid_submission):
        s1 = valid_submission.copy()
        s2 = valid_submission.copy()
        s2["__system"] = {"instanceID": "uuid:def-456"}
        s3 = valid_submission.copy()
        s3["current_lga"] = "invalid_lga"

        result = ODKBridge.process_bulk([s1, s2, s3])
        assert result["created_count"] == 2
        assert result["error_count"] == 1
        assert result["duplicate_count"] == 0

    def test_bulk_duplicate(self, lga_aba_north, valid_submission):
        ODKBridge.process_submission(valid_submission)
        result = ODKBridge.process_bulk([valid_submission])
        assert result["duplicate_count"] == 1
        assert result["created_count"] == 0


@pytest.mark.django_db
class TestConflictResolution:
    def test_resolve_updates_existing(self, lga_aba_north, valid_submission):
        original = ODKBridge.process_submission(valid_submission)
        updated = ODKBridge.resolve_conflict("uuid:abc-123", {
            "full_name": "Jane Doe",
            "household_size": 6,
        })
        assert updated.id == original.id
        assert updated.full_name == "Jane Doe"
        assert updated.household_size == 6

    def test_resolve_missing_raises(self):
        with pytest.raises(InvalidSubmissionError):
            ODKBridge.resolve_conflict("uuid:nonexistent", {})
