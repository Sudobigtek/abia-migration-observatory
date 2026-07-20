from rest_framework import serializers
from .models import ChartDashboard

class ChartDashboardSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = ChartDashboard
        fields = ["id", "name", "chart_type", "data_source", "query_config", "chart_config",
                  "is_public", "created_by", "created_by_name", "created_at", "updated_at"]