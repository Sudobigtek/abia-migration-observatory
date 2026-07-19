import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"), ("update", "Update"), ("delete", "Delete"),
        ("view", "View"), ("export", "Export"), ("login", "Login"),
        ("logout", "Logout"), ("failed_login", "Failed Login"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100, blank=True)
    entity_repr = models.CharField(max_length=255, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["ip_address", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action.upper()} {self.entity_type} by {self.user} at {self.created_at}"

class ComplianceReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ("monthly", "Monthly"), ("quarterly", "Quarterly"),
        ("annual", "Annual"), ("ad_hoc", "Ad-hoc"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    data = models.JSONField(default=dict)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-generated_at"]