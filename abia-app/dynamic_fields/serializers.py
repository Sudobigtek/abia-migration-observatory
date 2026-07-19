from rest_framework import serializers
from .models import DynamicFieldDefinition, EntityDynamicData


class DynamicFieldDefinitionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = DynamicFieldDefinition
        fields = [
            'id', 'entity_type', 'field_name', 'field_label', 'field_type',
            'choices', 'is_required', 'is_active', 'order', 'help_text',
            'validation_regex', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EntityDynamicDataSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field_definition.field_name', read_only=True)
    field_label = serializers.CharField(source='field_definition.field_label', read_only=True)
    entity_type = serializers.CharField(source='field_definition.entity_type', read_only=True)

    class Meta:
        model = EntityDynamicData
        fields = [
            'id', 'entity_type', 'entity_id', 'field_definition',
            'field_name', 'field_label', 'value_text', 'value_number',
            'value_boolean', 'value_date', 'value_json', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EntityDynamicDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityDynamicData
        fields = ['entity_id', 'field_definition', 'value_text', 'value_number', 'value_boolean', 'value_date', 'value_json']


class BulkDynamicDataSerializer(serializers.Serializer):
    entity_type = serializers.CharField(max_length=50)
    entity_id = serializers.UUIDField()
    fields = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(), allow_empty=False),
        allow_empty=False
    )
