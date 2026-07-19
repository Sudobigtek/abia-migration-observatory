from rest_framework import serializers
from .models import HotspotPrediction

class HotspotPredictionSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    class Meta:
        model = HotspotPrediction
        fields = ["id", "lga", "lga_name", "risk_level", "risk_score",
                  "predicted_migrant_count", "contributing_factors",
                  "analysis_period_start", "analysis_period_end", "created_at"]