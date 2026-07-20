from rest_framework import serializers
from .models import BackupJob, RestoreJob

class BackupJobSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = BackupJob
        fields = ["id", "backup_type", "status", "file_path", "file_size", "checksum",
                  "tables_backed_up", "row_count", "error_message", "started_at",
                  "completed_at", "created_by", "created_by_name", "created_at"]

class RestoreJobSerializer(serializers.ModelSerializer):
    backup_id = serializers.UUIDField(source="backup.id", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = RestoreJob
        fields = ["id", "backup", "backup_id", "status", "tables_restored", "row_count",
                  "error_message", "started_at", "completed_at", "created_by",
                  "created_by_name", "created_at"]