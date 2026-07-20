import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class IOMDataExchange(models.Model):
    DIRECTION_CHOICES = [
        ("outbound", "To IOM"),
        ("inbound", "From IOM"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("rejected", "Rejected by IOM"),
    ]
    ENTITY_TYPES = [
        ("migrant", "Migrant Profile"),
        ("case", "Case Record"),
        ("referral", "Referral"),
        ("assessment", "Needs Assessment"),
        ("protection", "Protection Incident"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    entity_id = models.CharField(max_length=100, help_text="Local entity ID")
    iom_reference = models.CharField(max_length=100, blank=True, help_text="IOM system reference")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payload = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "status"]),
            models.Index(fields=["direction", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.direction} {self.entity_type} - {self.status}"

class IOMConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_base_url = models.URLField(default="https://api.iom.int/v1")
    api_key = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=100, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    sync_interval_hours = models.PositiveIntegerField(default=24)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IOM Configuration"
        verbose_name_plural = "IOM Configurations"

    def __str__(self):
        return f"IOM Config ({self.api_base_url})"