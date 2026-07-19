import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NCFRMISyncLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("synced", "Synced"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrant = models.ForeignKey("migrants.Migrant", on_delete=models.CASCADE, related_name="ncfrmi_syncs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    ncfrmi_record_id = models.CharField(max_length=100, blank=True)
    sync_payload = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    synced_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["migrant", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"Sync {self.migrant} - {self.status}"