from rest_framework import serializers
from .models import ECOWASMigrantFlow, ECOWASTradeFlow, ECOWASConfiguration

class ECOWASMigrantFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECOWASMigrantFlow
        fields = ["id", "country_of_origin", "country_of_destination", "migration_type", "sector",
                  "gender", "age_group", "estimated_count", "year", "protocol_article", "data_source", "created_at"]

class ECOWASTradeFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECOWASTradeFlow
        fields = ["id", "reporter_country", "partner_country", "product_category",
                  "export_value", "import_value", "year", "data_source", "created_at"]

class ECOWASConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECOWASConfiguration
        fields = ["id", "api_base_url", "api_key", "is_active", "auto_sync_enabled", "last_sync_at"]
        extra_kwargs = {"api_key": {"write_only": True}}