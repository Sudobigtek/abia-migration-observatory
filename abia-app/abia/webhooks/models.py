import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WebhookEndpoint(models.Model):
    EVENT_TYPES = [
        ("migrant.created", "Migrant Created"),
        ("migrant.updated", "Migrant Updated"),
        ("case.created", "Case Created"),
        ("case.updated", "Case Updated"),
        ("case.resolved", "Case Resolved"),
        ("referral.created", "Referral Created"),
        ("referral.completed", "Referral Completed"),
        ("sync.completed", "Sync Completed"),
        ("sync.failed", "Sync Failed"),
        ("hotspot.critical", "Critical Hotspot Detected"),
        ("all", "All Events"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(help_text="Webhook receiver URL")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default="all")
    secret = models.CharField(max_length=255, blank=True, help_text="HMAC secret for signing")
    is_active = models.BooleanField(default=True)
    retry_count = models.PositiveIntegerField(default=3)
    timeout_seconds = models.PositiveIntegerField(default=30)
    headers = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.event_type})"

class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="deliveries")
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["webhook", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["event_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} to {self.webhook.name} - {self.status}"