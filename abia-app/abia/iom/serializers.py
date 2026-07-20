from rest_framework import serializers
from .models import IOMDataExchange, IOMConfiguration

class IOMDataExchangeSerializer(serializers.ModelSerializer):
    processed_by_name = serializers.CharField(source="processed_by.get_full_name", read_only=True)
    class Meta:
        model = IOMDataExchange
        fields = ["id", "direction", "entity_type", "entity_id", "iom_reference", "status",
                  "payload", "response_data", "error_message", "retry_count",
                  "processed_by", "processed_by_name", "created_at", "updated_at"]

class IOMConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IOMConfiguration
        fields = ["id", "api_base_url", "api_key", "client_id", "client_secret",
                  "is_active", "auto_sync_enabled", "sync_interval_hours", "last_sync_at",
                  "created_at", "updated_at"]
        extra_kwargs = {"client_secret": {"write_only": True}, "api_key": {"write_only": True}}