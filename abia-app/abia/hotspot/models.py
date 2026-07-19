import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models

class HotspotPrediction(models.Model):
    RISK_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lga = models.ForeignKey("accounts.LGA", on_delete=models.CASCADE, related_name="hotspot_predictions")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_score = models.FloatField(help_text="0.0 to 1.0")
    predicted_migrant_count = models.PositiveIntegerField()
    contributing_factors = models.JSONField(default=dict, help_text="AI-identified risk factors")
    centroid = gis_models.PointField(null=True, blank=True, srid=4326)
    analysis_period_start = models.DateField()
    analysis_period_end = models.DateField()
    model_version = models.CharField(max_length=50, default="v1.0")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-risk_score", "-created_at"]
        indexes = [
            models.Index(fields=["lga", "-risk_score"]),
            models.Index(fields=["risk_level", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.lga} - {self.risk_level} ({self.risk_score:.2f})"