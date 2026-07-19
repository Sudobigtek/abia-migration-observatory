from rest_framework import serializers
from .models import DataQualityRule, DataQualityIssue

class DataQualityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataQualityRule
        fields = ['id', 'name', 'rule_type', 'model_name', 'field_name', 'condition', 'severity', 'is_active', 'auto_fix', 'created_at']
        read_only_fields = ['id', 'created_at']

class DataQualityIssueSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = DataQualityIssue
        fields = ['id', 'rule', 'rule_name', 'model_name', 'record_id', 'field_name', 'issue_description', 'current_value', 'suggested_value', 'status', 'resolved_by', 'resolved_at', 'created_at']
        read_only_fields = ['id', 'created_at']
