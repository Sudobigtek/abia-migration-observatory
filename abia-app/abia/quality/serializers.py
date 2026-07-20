from rest_framework import serializers
from .models import DataQualityRule, DataQualityIssue

class DataQualityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataQualityRule
        fields = ["id", "name", "rule_type", "entity_type", "field_name", "condition", "parameters", "is_active", "severity", "created_at"]

class DataQualityIssueSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    class Meta:
        model = DataQualityIssue
        fields = ["id", "rule", "rule_name", "entity_type", "entity_id", "field_name", "issue_description", "severity", "status", "resolved_by", "resolved_at", "created_at"]