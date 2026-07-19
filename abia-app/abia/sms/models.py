import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SMSCampaign(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sending", "Sending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    message = models.TextField()
    target_lgas = models.ManyToManyField("geo.LGA", blank=True, related_name="sms_campaigns")
    target_status = models.CharField(max_length=50, blank=True, help_text="Migrant status filter")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    provider = models.CharField(max_length=50, default="africastalking",
                                choices=[("africastalking", "AfricasTalking"), ("twilio", "Twilio")])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sms_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

class SMSLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("bounced", "Bounced"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    recipient = models.ForeignKey("migrants.Migrant", on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campaign", "status"]),
            models.Index(fields=["phone", "-created_at"]),
        ]
