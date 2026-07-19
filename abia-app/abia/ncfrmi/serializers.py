from rest_framework import serializers
from .models import NCFRMISyncLog

class NCFRMISyncLogSerializer(serializers.ModelSerializer):
    migrant_name = serializers.CharField(source="migrant.full_name", read_only=True)
    synced_by_name = serializers.CharField(source="synced_by.get_full_name", read_only=True)
    class Meta:
        model = NCFRMISyncLog
        fields = ["id", "migrant", "migrant_name", "status",
                  "ncfrmi_record_id", "sync_payload", "response_data",
                  "error_message", "retry_count", "synced_by",
                  "synced_by_name", "created_at", "updated_at"]