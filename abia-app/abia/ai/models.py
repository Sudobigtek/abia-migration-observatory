import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RiskAssessment(models.Model):
    RISK_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrant = models.ForeignKey("migrants.Migrant", on_delete=models.CASCADE, related_name="risk_assessments")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default="low")
    risk_score = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    factors = models.JSONField(default=dict, help_text="Detected risk factors")
    recommendations = models.JSONField(default=list, help_text="AI recommendations")
    model_version = models.CharField(max_length=50, default="ollama:llama3")
    raw_response = models.JSONField(default=dict, blank=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["risk_level", "created_at"]),
            models.Index(fields=["migrant", "-created_at"]),
        ]

    def __str__(self):
        return f"Risk: {self.risk_level.upper()} ({self.risk_score:.2f}) - {self.migrant.full_name}"

class AIPredictionLog(models.Model):
    PREDICTION_TYPES = [
        ("risk_assessment", "Risk Assessment"),
        ("case_priority", "Case Priority"),
        ("referral_match", "Referral Match"),
        ("fraud_detection", "Fraud Detection"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    input_data = models.JSONField()
    output_data = models.JSONField()
    confidence = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100)
    latency_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

# Backward compatibility alias
PredictionLog = AIPredictionLog
