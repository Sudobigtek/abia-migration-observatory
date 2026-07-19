import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('case_critical', 'Critical Case Alert'),
        ('case_assigned', 'Case Assigned'),
        ('case_resolved', 'Case Resolved'),
        ('referral_pending', 'Referral Pending'),
        ('referral_accepted', 'Referral Accepted'),
        ('referral_completed', 'Referral Completed'),
        ('risk_high', 'High Risk Alert'),
        ('risk_critical', 'Critical Risk Alert'),
        ('system', 'System Notification'),
    ]

    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
        ('push', 'Push Notification'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS, default='in_app')
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_object_type = models.CharField(max_length=50, blank=True, help_text="e.g., 'case', 'referral', 'migrant'")
    related_object_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient.username} ({self.status})"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    case_critical_email = models.BooleanField(default=True)
    case_critical_sms = models.BooleanField(default=False)
    referral_updates_email = models.BooleanField(default=True)
    risk_alerts_email = models.BooleanField(default=True)
    risk_alerts_sms = models.BooleanField(default=False)
    daily_digest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
