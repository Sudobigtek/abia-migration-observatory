import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ReportTemplate(models.Model):
    REPORT_TYPES = [
        ("migrants", "Migrant Report"),
        ("cases", "Case Report"),
        ("referrals", "Referral Report"),
        ("analytics", "Analytics Report"),
        ("custom", "Custom Report"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    query_config = models.JSONField(default=dict, help_text="Filter and aggregation config")
    chart_config = models.JSONField(default=dict, blank=True, help_text="Chart.js config")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class GeneratedReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name="generated_reports")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    parameters = models.JSONField(default=dict)
    data = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_format = models.CharField(max_length=10, default="pdf", choices=[("pdf", "PDF"), ("csv", "CSV"), ("xlsx", "Excel")])
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"