import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DataQualityRule(models.Model):
    RULE_TYPES = [
        ('required_field', 'Required Field Check'),
        ('format', 'Format Validation'),
        ('duplicate', 'Duplicate Detection'),
        ('consistency', 'Cross-Record Consistency'),
        ('range', 'Value Range Check'),
    ]

    SEVERITY_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    model_name = models.CharField(max_length=50, help_text="e.g., 'migrants.Migrant'")
    field_name = models.CharField(max_length=100, blank=True)
    condition = models.JSONField(default=dict, help_text="Rule condition as JSON")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='error')
    is_active = models.BooleanField(default=True)
    auto_fix = models.BooleanField(default=False, help_text="Attempt automatic fix")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.model_name})"

class DataQualityIssue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(DataQualityRule, on_delete=models.CASCADE, related_name='issues')
    model_name = models.CharField(max_length=50)
    record_id = models.UUIDField()
    field_name = models.CharField(max_length=100, blank=True)
    issue_description = models.TextField()
    current_value = models.TextField(blank=True)
    suggested_value = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'model_name']),
            models.Index(fields=['record_id']),
        ]
