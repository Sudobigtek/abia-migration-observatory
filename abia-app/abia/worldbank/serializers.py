from rest_framework import serializers
from .models import WBIndicator, WBDataPoint, WBConfiguration

class WBIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = WBIndicator
        fields = ["id", "indicator_code", "indicator_name", "description", "category", "unit", "is_active"]

class WBDataPointSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source="indicator.indicator_name", read_only=True)
    class Meta:
        model = WBDataPoint
        fields = ["id", "indicator", "indicator_name", "country_code", "country_name", "year", "value", "last_updated"]

class WBConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WBConfiguration
        fields = ["id", "api_base_url", "api_key", "is_active", "auto_sync_enabled", "last_sync_at"]
        extra_kwargs = {"api_key": {"write_only": True}}