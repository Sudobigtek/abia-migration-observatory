import uuid

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models


class Case(models.Model):
    TYPES = [
        ("irregular_migration", "Irregular Migration"),
        ("trafficking", "Human Trafficking"),
        ("smuggling", "Migrant Smuggling"),
        ("refugee_status", "Refugee Status"),
        ("internal_displacement", "Internal Displacement"),
        ("returnee_reintegration", "Returnee Reintegration"),
        ("skills_training", "Skills Training"),
        ("legal_aid", "Legal Aid"),
        ("healthcare", "Healthcare"),
        ("other", "Other"),
    ]
    STATUS = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("escalated", "Escalated"),
        ("closed", "Closed"),
    ]
    PRIORITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrant = models.ForeignKey(
        "migrants.Migrant", on_delete=models.CASCADE, related_name="cases"
    )
    case_type = models.CharField(max_length=50, choices=TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="open")
    priority = models.CharField(max_length=10, choices=PRIORITY, default="medium")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_cases",
    )
    lga = models.ForeignKey(
        "accounts.LGA", on_delete=models.PROTECT, related_name="cases"
    )
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    documents = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cases_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if not self.migrant_id:
            raise ValidationError({"migrant": "Migrant is required."})
        if not self.lga_id:
            raise ValidationError({"lga": "LGA is required."})

    class Meta:
        app_label = "cases"
        ordering = ["-created_at"]
