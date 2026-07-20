from rest_framework import serializers
from .models import TradeRecord, WTOConfiguration

class TradeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeRecord
        fields = ["id", "flow_type", "product_category", "hs_code", "sector", "value_usd",
                  "quantity", "trade_partner", "partner_country_code", "year", "quarter",
                  "labour_intensity_score", "data_source", "created_at"]

class WTOConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WTOConfiguration
        fields = ["id", "api_base_url", "api_key", "is_active", "auto_sync_enabled", "last_sync_at"]
        extra_kwargs = {"api_key": {"write_only": True}}