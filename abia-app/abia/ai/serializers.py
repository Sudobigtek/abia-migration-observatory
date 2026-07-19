from rest_framework import serializers
from .models import RiskAssessment, AIPredictionLog

class RiskAssessmentSerializer(serializers.ModelSerializer):
    migrant_name = serializers.CharField(source="migrant.full_name", read_only=True)
    assessed_by_name = serializers.CharField(source="assessed_by.get_full_name", read_only=True)

    class Meta:
        model = RiskAssessment
        fields = [
            "id", "migrant", "migrant_name", "risk_level", "risk_score",
            "factors", "recommendations", "model_version",
            "assessed_by", "assessed_by_name", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

class AIPredictionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPredictionLog
        fields = [
            "id", "prediction_type", "confidence", "model_used",
            "latency_ms", "success", "created_at"
        ]
