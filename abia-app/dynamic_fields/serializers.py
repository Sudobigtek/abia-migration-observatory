from rest_framework import serializers
from .models import DynamicFieldDefinition, EntityDynamicData


class DynamicFieldDefinitionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = DynamicFieldDefinition
        fields = [
            "id", "entity_type", "field_name", "field_type", "label",
            "description", "choices", "default_value", "is_required",
            "is_sensitive", "is_searchable", "partner_org", "category",
            "validation_regex", "min_value", "max_value", "max_length",
            "order", "is_active", "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EntityDynamicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityDynamicData
        fields = ["id", "entity_type", "entity_id", "data", "search_vector", "updated_at"]
        read_only_fields = ["id", "search_vector", "updated_at"]


class EntityDynamicDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityDynamicData
        fields = ["entity_type", "entity_id", "data"]


class BulkDynamicDataSerializer(serializers.Serializer):
    entity_type = serializers.CharField(max_length=50)
    entity_id = serializers.IntegerField()
    fields = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField(), allow_empty=False),
        allow_empty=False
    )
