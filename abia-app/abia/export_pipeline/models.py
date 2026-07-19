import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DataExport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    FORMAT_CHOICES = [
        ("csv", "CSV"),
        ("json", "JSON"),
        ("excel", "Excel"),
        ("geojson", "GeoJSON"),
        ("ipfs", "IPFS"),
    ]
    ENTITY_CHOICES = [
        ("migrants", "Migrants"),
        ("cases", "Cases"),
        ("referrals", "Referrals"),
        ("all", "All Entities"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    export_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    filters = models.JSONField(default=dict, blank=True, help_text="Query filters")
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    record_count = models.IntegerField(null=True, blank=True)
    ipfs_hash = models.CharField(max_length=100, blank=True, db_index=True)
    ipfs_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)
    is_scheduled = models.BooleanField(default=False)
    cron_expression = models.CharField(max_length=100, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="data_exports")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["ipfs_hash"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.export_format})"
