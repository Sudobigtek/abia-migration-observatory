import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DataQualityRule(models.Model):
    RULE_TYPES = [
        ("completeness", "Completeness"),
        ("uniqueness", "Uniqueness"),
        ("validity", "Validity"),
        ("consistency", "Consistency"),
        ("timeliness", "Timeliness"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    entity_type = models.CharField(max_length=50, help_text="e.g. migrants.Migrant")
    field_name = models.CharField(max_length=100)
    condition = models.CharField(max_length=255, help_text="e.g. not_null, unique, regex")
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    severity = models.CharField(max_length=20, default="warning", choices=[("info", "Info"), ("warning", "Warning"), ("error", "Error")])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rule_type})"

class DataQualityIssue(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("ignored", "Ignored"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(DataQualityRule, on_delete=models.CASCADE, related_name="issues")
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    issue_description = models.TextField()
    severity = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "severity"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.field_name} - {self.issue_description[:50]}"