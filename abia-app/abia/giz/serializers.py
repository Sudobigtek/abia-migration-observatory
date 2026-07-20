from rest_framework import serializers
from .models import GIZDataExchange, GIZIndicator

class GIZDataExchangeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = GIZDataExchange
        fields = ["id", "programme_area", "title", "description", "data_payload", "status",
                  "giz_project_code", "giz_feedback", "submitted_at", "reviewed_at",
                  "created_by", "created_by_name", "created_at", "updated_at"]

class GIZIndicatorSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    class Meta:
        model = GIZIndicator
        fields = ["id", "name", "description", "category", "target_value", "current_value",
                  "unit", "programme_area", "reporting_period", "progress_percentage", "is_active"]