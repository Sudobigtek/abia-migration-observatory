import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WebhookEndpoint(models.Model):
    EVENT_CHOICES = [
        ('migrant.created', 'Migrant Created'),
        ('migrant.updated', 'Migrant Updated'),
        ('case.created', 'Case Created'),
        ('case.updated', 'Case Updated'),
        ('case.critical', 'Case Critical'),
        ('referral.created', 'Referral Created'),
        ('referral.completed', 'Referral Completed'),
        ('risk.assessed', 'Risk Assessment Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField(help_text="Target URL for webhook delivery")
    events = models.JSONField(default=list, help_text="List of event types to subscribe to")
    secret = models.CharField(max_length=255, blank=True, help_text="HMAC secret for signature verification")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} -> {self.url}"

class WebhookDelivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempts = models.PositiveSmallIntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
