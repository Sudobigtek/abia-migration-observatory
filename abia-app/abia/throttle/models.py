import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RateLimitLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    was_throttled = models.BooleanField(default=False)
    request_count = models.PositiveIntegerField(default=1)
    window_start = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ip_address", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["endpoint", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.endpoint} ({self.request_count})"