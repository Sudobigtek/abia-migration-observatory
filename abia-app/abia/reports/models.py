import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ReportTemplate(models.Model):
    REPORT_TYPES = [
        ('monthly', 'Monthly Summary'),
        ('quarterly', 'Quarterly Review'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
        ('lga', 'LGA Breakdown'),
        ('risk', 'Risk Analysis'),
        ('referral', 'Referral Performance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    query_config = models.JSONField(default=dict, help_text="JSON config for report query")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class GeneratedReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    name = models.CharField(max_length=255)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    parameters = models.JSONField(default=dict, help_text="Report parameters (date range, filters)")
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
