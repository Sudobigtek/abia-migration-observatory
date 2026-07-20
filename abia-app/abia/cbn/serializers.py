from rest_framework import serializers
from .models import RemittanceRecord, CBNConfiguration

class RemittanceRecordSerializer(serializers.ModelSerializer):
    recipient_lga_name = serializers.CharField(source="recipient_lga.name", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)
    class Meta:
        model = RemittanceRecord
        fields = ["id", "sender_name", "sender_country", "amount_sent", "naira_equivalent",
                  "recipient_name", "recipient_lga", "recipient_lga_name", "recipient_phone",
                  "channel", "bank_name", "transaction_reference", "transaction_date",
                  "purpose", "status", "verified_by_cbn", "recorded_by", "recorded_by_name", "created_at"]

class CBNConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBNConfiguration
        fields = ["id", "api_base_url", "api_key", "client_id", "is_active", "auto_sync_enabled", "last_sync_at"]
        extra_kwargs = {"api_key": {"write_only": True}, "client_secret": {"write_only": True}}