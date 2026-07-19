"""Tests for ODK sync conflict resolution."""

import pytest

from abia.common.exceptions import LGANotFoundError
from abia.migrants.odk_sync import ODKSyncResolver
from abia.migrants.models import Migrant, MigrantVersion, PhotoUploadQueue


@pytest.mark.django_db
class TestODKSyncResolver:
    """Test conflict resolution per Architecture Contract §16.2."""

    def test_resolve_officer_edit_creates_version(self, test_user):
        """Given edit after sync, create MigrantVersion."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()

        migrant = Migrant.objects.create(
            full_name="Original",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )

        edit_data = {"full_name": "Updated Name", "phone": "+2348222222222"}
        version = ODKSyncResolver.resolve_officer_edit(
            migrant, edit_data, test_user
        )

        assert isinstance(version, MigrantVersion)
        assert version.migrant == migrant
        assert version.full_name == "Updated Name"
        assert version.phone == "+2348222222222"
        assert "full_name" in version.change_summary
        assert MigrantVersion.objects.filter(migrant=migrant).count() == 1

    def test_resolve_lga_change_success(self, test_user):
        """Given valid LGA name, return LGA object."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()

        resolved = ODKSyncResolver.resolve_lga_change(lga.name)
        assert resolved == lga

    def test_resolve_lga_change_not_found(self):
        """Given invalid LGA, raise LGANotFoundError."""
        with pytest.raises(LGANotFoundError):
            ODKSyncResolver.resolve_lga_change("FakeLGA12345")

    def test_queue_photo_upload_new(self, test_user):
        """Given failed photo, create queue entry."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Photo Test",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )

        entry = ODKSyncResolver.queue_photo_upload(
            migrant, "/photos/test.jpg", "Network timeout"
        )

        assert isinstance(entry, PhotoUploadQueue)
        assert entry.status == "pending"
        assert entry.retry_count == 0
        assert entry.migrant == migrant

    def test_queue_photo_upload_retry_then_fail(self, test_user):
        """Given 3 retries (4 total calls), mark as failed for manual upload."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Retry Test",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )

        # Initial + 3 retries = 4 calls total
        for i in range(4):
            entry = ODKSyncResolver.queue_photo_upload(
                migrant, "/photos/retry.jpg", f"Error {i+1}"
            )

        assert entry.retry_count == 3
        assert entry.status == "failed"

    def test_build_change_summary(self, test_user):
        """Given edit data, build human-readable summary."""
        from abia.accounts.models import LGA
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Summary Test",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )

        edit_data = {"full_name": "New Name", "phone": "+2348999999999"}
        summary = ODKSyncResolver._build_change_summary(migrant, edit_data)

        assert "full_name: Summary Test → New Name" in summary
        assert "phone:" in summary
