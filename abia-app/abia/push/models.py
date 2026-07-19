import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PushDevice(models.Model):
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web Browser'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_devices')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    device_token = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_used']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_token']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.device_name}"

class PushNotification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_notifications')
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
