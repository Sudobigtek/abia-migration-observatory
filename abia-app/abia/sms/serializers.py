from rest_framework import serializers
from .models import SMSCampaign, SMSLog

class SMSCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    target_lga_names = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = SMSCampaign
        fields = [
            "id", "name", "message", "target_lgas", "target_lga_names",
            "target_status", "scheduled_at", "status", "total_recipients",
            "sent_count", "failed_count", "progress_pct", "provider",
            "created_by", "created_by_name", "created_at"
        ]
        read_only_fields = ["id", "created_at", "sent_count", "failed_count", "total_recipients"]

    def get_target_lga_names(self, obj):
        return [lga.name for lga in obj.target_lgas.all()]

    def get_progress_pct(self, obj):
        if obj.total_recipients == 0:
            return 0
        return round((obj.sent_count / obj.total_recipients) * 100, 1)

class SMSLogSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)

    class Meta:
        model = SMSLog
        fields = [
            "id", "campaign", "campaign_name", "recipient", "recipient_name",
            "phone", "message", "status", "sent_at", "delivered_at", "created_at"
        ]
