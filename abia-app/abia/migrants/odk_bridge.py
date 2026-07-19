"""ODK Collect → ODK Central → Django sync bridge.

Per Architecture Contract §2.4 (Data Collection) and §16 (Offline-First Field Data).
"""

import logging
from typing import Optional

from django.contrib.gis.geos import Point

from abia.accounts.models import LGA
from abia.common.exceptions import (
    DuplicateSubmissionError,
    InvalidGPSDataError,
    LGANotFoundError,
)

from .models import Migrant
from .repositories import MigrantRepository

logger = logging.getLogger("abia.odk")


class ODKBridge:
    """Process ODK submissions and create Migrant records."""

    @staticmethod
    def process_submission(submission_data: dict, created_by) -> Migrant:
        """Process raw ODK submission JSON.

        Called via webhook from ODK Central when a field officer
        submits a completed form. Handles GPS coordinate parsing,
        LGA validation, and duplicate detection.

        Args:
            submission_data: Raw ODK submission JSON containing
                form fields and metadata.

        Returns:
            Migrant: The newly created migrant record.

        Raises:
            LGANotFoundError: If current_lga in submission does not exist.
            DuplicateSubmissionError: If odk_submission_id already processed.
            InvalidGPSDataError: If GPS string is malformed.
        """
        instance_id = ODKBridge._extract_submission_id(submission_data)
        if MigrantRepository.exists_by_odk_submission_id(instance_id):
            raise DuplicateSubmissionError(
                f"ODK submission {instance_id} already processed."
            )

        data = submission_data.get("data", submission_data)
        lga = ODKBridge._resolve_lga(data)
        coordinates = ODKBridge._parse_gps(data)

        migrant_data = {
            "full_name": data.get("full_name") or data.get("name", ""),
            "phone": data.get("phone") or data.get("phone_number"),
            "gender": (data.get("gender") or "unknown").lower(),
            "date_of_birth": data.get("date_of_birth") or data.get("dob"),
            "current_lga": lga,
            "odk_submission_id": instance_id,
            "gps_coordinates": coordinates,
            "created_by": created_by,
        }

        return MigrantRepository.create_from_odk(migrant_data)

    @staticmethod
    def _extract_submission_id(submission_data: dict) -> str:
        """Extract ODK instance ID from submission metadata."""
        meta = submission_data.get("meta", {})
        instance_id = meta.get("instanceID") or submission_data.get("__id")
        if not instance_id:
            raise ValueError("Submission missing instanceID or __id")
        return str(instance_id)

    @staticmethod
    def _parse_gps(data: dict) -> Optional[Point]:
        """Parse ODK GPS string 'lat lon alt acc' into GeoDjango Point."""
        gps_str = data.get("gps") or data.get("location")
        if not gps_str:
            return None
        parts = str(gps_str).strip().split()
        if len(parts) < 2:
            raise InvalidGPSDataError(f"GPS string '{gps_str}' has <2 coordinates")
        try:
            lat, lon = float(parts[0]), float(parts[1])
            return Point(lon, lat, srid=4326)
        except ValueError as exc:
            raise InvalidGPSDataError(f"Cannot parse GPS '{gps_str}': {exc}") from exc

    @staticmethod
    def _resolve_lga(data: dict) -> LGA:
        """Resolve LGA by name or spatial query."""
        lga_name = data.get("current_lga") or data.get("lga")
        if lga_name:
            lga = LGA.objects.filter(name__iexact=lga_name.strip()).first()
            if lga:
                return lga
        raise LGANotFoundError(f"LGA '{lga_name}' not found in database.")
