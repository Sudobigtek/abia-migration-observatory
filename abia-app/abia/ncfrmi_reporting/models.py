import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NCFRMIMonthlyReport(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("approved", "Approved by State Coordinator"),
        ("submitted", "Submitted to NCFRMI Abuja"),
        ("acknowledged", "Acknowledged by NCFRMI"),
        ("rejected", "Rejected"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_month = models.PositiveIntegerField(help_text="1-12")
    report_year = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    summary = models.TextField()
    total_migrants_registered = models.PositiveIntegerField(default=0)
    total_cases_opened = models.PositiveIntegerField(default=0)
    total_cases_resolved = models.PositiveIntegerField(default=0)
    total_referrals_made = models.PositiveIntegerField(default=0)
    total_referrals_completed = models.PositiveIntegerField(default=0)
    returnees_assisted = models.PositiveIntegerField(default=0)
    vulnerable_cases_identified = models.PositiveIntegerField(default=0)
    protection_incidents = models.PositiveIntegerField(default=0)
    hotspot_alerts_issued = models.PositiveIntegerField(default=0)
    lga_breakdown = models.JSONField(default=dict, blank=True)
    challenges = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    submitted_to_ncfrmi_at = models.DateTimeField(null=True, blank=True)
    ncfrmi_reference = models.CharField(max_length=100, blank=True)
    prepared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ncfrmi_reports")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_ncfrmi_reports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_year", "-report_month"]
        unique_together = [["report_month", "report_year", "prepared_by"]]
        indexes = [
            models.Index(fields=["status", "-report_year", "-report_month"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.report_month}/{self.report_year})"

class NCFRMISubmissionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(NCFRMIMonthlyReport, on_delete=models.CASCADE, related_name="submission_logs")
    action = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} on {self.report}"