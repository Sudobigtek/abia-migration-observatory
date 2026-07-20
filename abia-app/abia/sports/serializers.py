from rest_framework import serializers
from .models import AthleteProfile, AthleteTransfer, SportsConfiguration

class AthleteProfileSerializer(serializers.ModelSerializer):
    origin_lga_name = serializers.CharField(source="origin_lga.name", read_only=True)
    class Meta:
        model = AthleteProfile
        fields = ["id", "full_name", "date_of_birth", "gender", "nationality", "origin_lga",
                  "origin_lga_name", "sport", "position", "current_club", "current_country",
                  "market_value_usd", "is_active", "created_at", "updated_at"]

class AthleteTransferSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source="athlete.full_name", read_only=True)
    athlete_sport = serializers.CharField(source="athlete.sport", read_only=True)
    class Meta:
        model = AthleteTransfer
        fields = ["id", "athlete", "athlete_name", "athlete_sport", "from_club", "from_country",
                  "to_club", "to_country", "transfer_fee_usd", "transfer_type", "transfer_date",
                  "contract_end_date", "agent_name", "status", "is_international", "created_at"]

class SportsConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsConfiguration
        fields = ["id", "data_source_name", "api_base_url", "api_key", "is_active", "auto_sync_enabled", "last_sync_at"]
        extra_kwargs = {"api_key": {"write_only": True}}