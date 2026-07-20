import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GIZDataExchange(models.Model):
    PROGRAMME_AREAS = [
        ("migration_governance", "Migration Governance"),
        ("labour_migration", "Labour Migration"),
        ("diaspora_engagement", "Diaspora Engagement"),
        ("protection_assistance", "Protection & Assistance"),
        ("reintegration", "Reintegration Support"),
        ("skills_development", "Skills Development"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted to GIZ"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("implemented", "Implemented"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    programme_area = models.CharField(max_length=30, choices=PROGRAMME_AREAS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data_payload = models.JSONField(default=dict, help_text="Structured data for GIZ reporting")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    giz_project_code = models.CharField(max_length=50, blank=True, help_text="GIZ project reference")
    giz_feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["programme_area", "status"]),
            models.Index(fields=["giz_project_code"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.programme_area})"

class GIZIndicator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default="general")
    target_value = models.PositiveIntegerField(default=0)
    current_value = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="count")
    programme_area = models.CharField(max_length=30, choices=GIZDataExchange.PROGRAMME_AREAS)
    reporting_period = models.CharField(max_length=50, default="Q3-2026")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["programme_area", "name"]

    def __str__(self):
        return f"{self.name} ({self.current_value}/{self.target_value})"

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return round((self.current_value / self.target_value) * 100, 2)