from rest_framework import serializers
from .models import ReportTemplate, GeneratedReport

class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ReportTemplate
        fields = ['id', 'name', 'report_type', 'description', 'query_config', 'is_active', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class GeneratedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = GeneratedReport
        fields = ['id', 'template', 'template_name', 'name', 'format', 'parameters', 'file_path', 'file_size', 'status', 'generated_by', 'generated_by_name', 'started_at', 'completed_at', 'created_at']
        read_only_fields = ['id', 'started_at', 'completed_at', 'created_at']
