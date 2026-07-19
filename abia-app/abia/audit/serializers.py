from rest_framework import serializers
from .models import AuditLog, ComplianceReport

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    class Meta:
        model = AuditLog
        fields = ["id", "user", "user_name", "action", "entity_type",
                  "entity_id", "entity_repr", "old_values", "new_values",
                  "ip_address", "reason", "created_at"]

class ComplianceReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)
    class Meta:
        model = ComplianceReport
        fields = ["id", "title", "report_type", "period_start", "period_end",
                  "data", "generated_by", "generated_by_name", "generated_at"]