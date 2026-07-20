from rest_framework import serializers
from .models import ImportJob

class ImportJobSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = ImportJob
        fields = ["id", "entity_type", "file_name", "status", "total_rows", "processed_rows",
                  "success_rows", "failed_rows", "error_log", "created_by", "created_by_name",
                  "created_at", "completed_at"]