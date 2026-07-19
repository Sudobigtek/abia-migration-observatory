import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db import models as gis_models


class Migrant(models.Model):
    GENDER = [("male", "Male"), ("female", "Female"), ("other", "Other")]
    STATUS = [
        ("active", "Active"),
        ("relocated", "Relocated"),
        ("deceased", "Deceased"),
        ("unknown", "Unknown"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    odk_submission_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    id_type = models.CharField(max_length=50, blank=True)
    id_number = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=100, default="Nigeria")
    state_of_origin = models.CharField(max_length=100, blank=True)
    lga_of_origin = models.CharField(max_length=100, blank=True)
    current_lga = models.ForeignKey(
        "accounts.LGA", on_delete=models.PROTECT, related_name="migrants"
    )
    current_address = models.TextField(blank=True)
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    photo_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="migrants_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        from abia.common.validators import validate_nigeria_phone

        super().clean()
        if self.phone:
            try:
                validate_nigeria_phone(self.phone)
            except ValidationError as e:
                raise ValidationError({"phone": e.message})
        if not self.current_lga_id:
            raise ValidationError({"current_lga": "Current LGA is required."})

    odk_submission_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="ODK Central submission ID for duplicate detection",
    )
    gps_coordinates = models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="GPS coordinates captured by ODK Collect",
    )

    id_number_encrypted = models.TextField(
        null=True,
        blank=True,
        help_text="AES-256 encrypted NIN or passport number",
    )
    id_number_plaintext = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Temporary plaintext (dev only — remove before production)",
    )

    class Meta:
        app_label = "migrants"
        ordering = ["-created_at"]


class MigrantVersion(models.Model):
    """Audit trail for migrant edits after ODK sync.

    Per Architecture Contract §16.2:
    Officer edits after sync → Create new version, keep history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrant = models.ForeignKey(
        Migrant, on_delete=models.CASCADE, related_name="versions"
    )
    edited_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    current_lga = models.ForeignKey(
        "accounts.LGA", on_delete=models.SET_NULL, null=True
    )
    change_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "migrants_migrantversion"


class PhotoUploadQueue(models.Model):
    """Queue for photos that failed to upload during ODK sync.

    Per Architecture Contract §16.2:
    Photo upload fails → Retry 3x, then queue for manual upload.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("retrying", "Retrying"),
        ("failed", "Failed — Manual Upload Required"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrant = models.ForeignKey(
        Migrant, on_delete=models.CASCADE, related_name="photo_queue"
    )
    photo_path = models.CharField(max_length=500)
    retry_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "migrants_photouploadqueue"
