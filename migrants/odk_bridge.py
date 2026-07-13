"""ODK Central → Django sync bridge.

Architecture Contract §2.4, §16.1, §16.2
"""

import logging
from datetime import date
from typing import Optional

from django.db import transaction
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

from .models import Migrant

logger = logging.getLogger(__name__)


class ODKBridge:
    """Bridge between ODK Central submissions and Django Migrant records."""

    @staticmethod
    def _parse_gps(gps_str: str) -> Optional[Point]:
        """Parse ODK geopoint string to PostGIS Point."""
        if not gps_str or not isinstance(gps_str, str):
            return None
        parts = gps_str.strip().split()
        if len(parts) < 2:
            return None
        try:
            lat, lon = float(parts[0]), float(parts[1])
            return Point(lon, lat, srid=4326)
        except (ValueError, IndexError):
            logger.warning("Invalid GPS: %s", gps_str)
            return None

    @staticmethod
    def _parse_date(dob_str: str) -> Optional[date]:
        """Parse ISO date string."""
        if not dob_str:
            return None
        try:
            return date.fromisoformat(dob_str.replace("/", "-"))
        except ValueError:
            logger.warning("Invalid date: %s", dob_str)
            return None

    @staticmethod
    def _resolve_lga(lga_code: str):
        """Find LGA by code, fallback to name."""
        if not lga_code:
            raise LGANotFoundError("LGA code is empty")
        try:
            return LGA.objects.get(code=lga_code)
        except LGA.DoesNotExist:
            try:
                return LGA.objects.get(name__iexact=lga_code.replace("_", " "))
            except LGA.DoesNotExist:
                raise LGANotFoundError(f"LGA '{lga_code}' not found")

    @staticmethod
    def process_submission(submission_data: dict) -> Migrant:
        """Process single ODK submission → Migrant record."""
        meta = submission_data.get("__system", {})
        instance_id = meta.get("instanceID") or submission_data.get("meta", {}).get("instanceID")

        if not instance_id:
            raise InvalidSubmissionError("Missing instanceID")

        if Migrant.objects.filter(odk_submission_id=instance_id).exists():
            raise DuplicateSubmissionError(f"Submission {instance_id} already processed")

        fields = submission_data
        current_lga = ODKBridge._resolve_lga(fields.get("current_lga", ""))

        origin_lga = None
        origin_code = fields.get("lga_of_origin")
        if origin_code:
            try:
                origin_lga = ODKBridge._resolve_lga(origin_code)
            except LGANotFoundError:
                logger.warning("Origin LGA %s not found", origin_code)

        location = ODKBridge._parse_gps(fields.get("gps_coords", ""))
        date_of_birth = ODKBridge._parse_date(fields.get("date_of_birth", ""))

        try:
            household_size = int(fields.get("household_size", 1) or 1)
        except (ValueError, TypeError):
            household_size = 1

        data = {
            "odk_submission_id": instance_id,
            "full_name": fields.get("full_name", "").strip(),
            "gender": fields.get("gender", ""),
            "date_of_birth": date_of_birth,
            "country_of_origin": fields.get("country_of_origin", ""),
            "state_of_origin": fields.get("state_of_origin", ""),
            "lga_of_origin": origin_lga,
            "current_lga": current_lga,
            "phone_number": fields.get("phone_number", ""),
            "id_number": fields.get("id_number", ""),
            "migrant_status": fields.get("migrant_status", ""),
            "services_needed": fields.get("services_needed", ""),
            "destination_intended": fields.get("destination_intended", ""),
            "location": location,
            "photo_url": fields.get("photo_ref", ""),
            "household_size": household_size,
            "is_vulnerable": fields.get("vulnerable") == "yes",
            "vulnerability_notes": fields.get("vulnerability_notes", ""),
            "enumerator_id": fields.get("enumerator_id", ""),
            "device_id": fields.get("deviceid", ""),
        }

        with transaction.atomic():
            migrant = Migrant.objects.create(**data)

        logger.info("Created migrant %s from ODK %s", migrant.id, instance_id)
        return migrant

    @staticmethod
    def process_bulk(submissions: list) -> dict:
        """Process multiple submissions with conflict resolution."""
        created, duplicates, errors = [], [], []

        for sub in submissions:
            try:
                migrant = ODKBridge.process_submission(sub)
                created.append(str(migrant.id))
            except DuplicateSubmissionError as e:
                duplicates.append(str(e))
            except Exception as e:
                logger.exception("ODK submission failed")
                errors.append(str(e))

        return {
            "created_count": len(created),
            "duplicate_count": len(duplicates),
            "error_count": len(errors),
            "created_ids": created,
            "duplicate_messages": duplicates,
            "error_messages": errors,
        }

    @staticmethod
    def resolve_conflict(instance_id: str, new_data: dict) -> Migrant:
        """Resolve edit conflict by updating existing record."""
        try:
            existing = Migrant.objects.get(odk_submission_id=instance_id)
        except Migrant.DoesNotExist:
            raise InvalidSubmissionError(f"No migrant for {instance_id}")

        logger.info("Updating migrant %s from ODK edit", existing.id)
        for key, value in new_data.items():
            if hasattr(existing, key) and key not in ("id", "odk_submission_id"):
                setattr(existing, key, value)
        existing.save()
        return existing
