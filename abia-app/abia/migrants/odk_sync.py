"""ODK sync conflict resolution and retry logic.

Per Architecture Contract §16.2:
- Duplicate submission → Ignore, log warning
- Officer edits after sync → Create new version, keep history
- LGA changed since last sync → Use latest LGA, flag for review
- Photo upload fails → Retry 3x, then queue for manual upload
"""

import logging
from typing import Optional

from abia.accounts.models import LGA
from abia.common.exceptions import LGANotFoundError

from .models import Migrant, MigrantVersion, PhotoUploadQueue

logger = logging.getLogger("abia.odk.sync")


class ODKSyncResolver:
    """Resolve conflicts and handle retries for ODK submissions."""

    MAX_PHOTO_RETRIES = 3

    @staticmethod
    def resolve_officer_edit(
        migrant: Migrant,
        edit_data: dict,
        edited_by,
    ) -> MigrantVersion:
        """Create a versioned snapshot when an officer edits after sync.

        Args:
            migrant: The existing migrant record.
            edit_data: Dict of changed fields.
            edited_by: User who made the edit.

        Returns:
            MigrantVersion: The new version record.
        """
        version = MigrantVersion.objects.create(
            migrant=migrant,
            edited_by=edited_by,
            full_name=edit_data.get("full_name", migrant.full_name),
            phone=edit_data.get("phone", migrant.phone),
            gender=edit_data.get("gender", migrant.gender),
            current_lga=edit_data.get("current_lga", migrant.current_lga),
            change_summary=ODKSyncResolver._build_change_summary(migrant, edit_data),
        )
        logger.info(
            "Created MigrantVersion %s for migrant %s by user %s",
            version.id,
            migrant.id,
            edited_by.id,
        )
        return version

    @staticmethod
    def resolve_lga_change(
        submission_lga_name: str,
        migrant: Optional[Migrant] = None,
    ) -> LGA:
        """Resolve LGA discrepancy between submission and latest data.

        If the LGA in the submission does not match the migrant's current
        LGA, use the latest LGA and flag for review.

        Args:
            submission_lga_name: LGA name from ODK submission.
            migrant: Existing migrant (if any).

        Returns:
            LGA: The resolved LGA object.

        Raises:
            LGANotFoundError: If the LGA name cannot be resolved.
        """
        lga = LGA.objects.filter(name__iexact=submission_lga_name.strip()).first()
        if not lga:
            raise LGANotFoundError(
                f"LGA '{submission_lga_name}' not found in database."
            )

        if migrant and migrant.current_lga_id and migrant.current_lga != lga:
            logger.warning(
                "LGA changed for migrant %s: %s → %s. Flagging for review.",
                migrant.id,
                migrant.current_lga.name,
                lga.name,
            )
        return lga

    @staticmethod
    def queue_photo_upload(
        migrant: Migrant,
        photo_path: str,
        error_message: str = "",
    ) -> PhotoUploadQueue:
        """Queue a photo for retry or manual upload.

        If retry_count < MAX_PHOTO_RETRIES, status is 'retrying'.
        Otherwise, status is 'failed' for manual intervention.

        Args:
            migrant: The migrant the photo belongs to.
            photo_path: Path or URL to the photo.
            error_message: Error from last upload attempt.

        Returns:
            PhotoUploadQueue: The queue entry.
        """
        existing = PhotoUploadQueue.objects.filter(
            migrant=migrant, photo_path=photo_path, status__in=["pending", "retrying"]
        ).first()

        if existing:
            existing.retry_count += 1
            existing.last_error = error_message
            if existing.retry_count >= ODKSyncResolver.MAX_PHOTO_RETRIES:
                existing.status = "failed"
                logger.warning(
                    "Photo %s for migrant %s failed after %s retries. "
                    "Manual upload required.",
                    photo_path,
                    migrant.id,
                    existing.retry_count,
                )
            else:
                existing.status = "retrying"
                logger.info(
                    "Retrying photo upload %s for migrant %s (attempt %s/%s)",
                    photo_path,
                    migrant.id,
                    existing.retry_count,
                    ODKSyncResolver.MAX_PHOTO_RETRIES,
                )
            existing.save()
            return existing

        queue_entry = PhotoUploadQueue.objects.create(
            migrant=migrant,
            photo_path=photo_path,
            last_error=error_message,
            status="pending",
        )
        logger.info(
            "Queued photo %s for migrant %s (new entry)", photo_path, migrant.id
        )
        return queue_entry

    @staticmethod
    def _build_change_summary(migrant: Migrant, edit_data: dict) -> str:
        """Build a human-readable summary of changes."""
        changes = []
        for field, new_value in edit_data.items():
            old_value = getattr(migrant, field, None)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        return "; ".join(changes) if changes else "No changes detected"
