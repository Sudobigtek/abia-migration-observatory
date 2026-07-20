import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BackupJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    BACKUP_TYPES = [
        ("full", "Full Database"),
        ("incremental", "Incremental"),
        ("schema", "Schema Only"),
        ("data", "Data Only"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default="full")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveBigIntegerField(default=0, help_text="Bytes")
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA-256")
    tables_backed_up = models.JSONField(default=list, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.backup_type} backup - {self.status}"

class RestoreJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name="restores")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    tables_restored = models.JSONField(default=list, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Restore from {self.backup} - {self.status}"