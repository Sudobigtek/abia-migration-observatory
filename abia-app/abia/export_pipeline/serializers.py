from rest_framework import serializers
from .models import DataExport

class DataExportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    format_display = serializers.CharField(source="get_export_format_display", read_only=True)

    class Meta:
        model = DataExport
        fields = [
            "id", "name", "entity_type", "export_format", "format_display",
            "filters", "file_path", "file_size", "record_count",
            "ipfs_hash", "ipfs_url", "status", "status_display",
            "is_scheduled", "cron_expression", "last_run_at", "next_run_at",
            "created_by", "created_by_name", "created_at", "completed_at"
        ]
        read_only_fields = [
            "id", "file_path", "file_size", "record_count",
            "ipfs_hash", "ipfs_url", "status", "created_at", "completed_at"
        ]
