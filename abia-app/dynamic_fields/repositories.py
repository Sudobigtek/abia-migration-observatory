from typing import Any, Dict, List, Optional

from django.db import connection

from .models import DynamicFieldDefinition, DynamicFieldValue, EntityDynamicData


class DynamicFieldRepository:
    @staticmethod
    def get_values_by_entity(entity_type, entity_id):
        return list(
            DynamicFieldValue.objects.filter(
                entity_type=entity_type, entity_id=entity_id
            )
            .select_related("definition")
            .values(
                "definition__field_name",
                "definition__field_type",
                "definition__label",
                "value",
                "encrypted_value",
                "updated_at",
            )
        )

    @staticmethod
    def get_entities_by_field_value(entity_type, field_name, value):
        return list(
            DynamicFieldValue.objects.filter(
                entity_type=entity_type, definition__field_name=field_name, value=value
            ).values_list("entity_id", flat=True)
        )

    @staticmethod
    def get_aggregate(entity_type, entity_id):
        try:
            agg = EntityDynamicData.objects.get(
                entity_type=entity_type, entity_id=entity_id
            )
            return agg.data
        except EntityDynamicData.DoesNotExist:
            return None

    @staticmethod
    def rebuild_aggregate(entity_type, entity_id):
        values = DynamicFieldValue.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).select_related("definition")
        data = {}
        search_parts = []
        for v in values:
            if v.definition.is_sensitive and v.encrypted_value:
                continue
            data[v.definition.field_name] = v.value
            if v.definition.is_searchable and v.value:
                search_parts.append(str(v.value))
        EntityDynamicData.objects.update_or_create(
            entity_type=entity_type,
            entity_id=entity_id,
            defaults={"data": data, "search_vector": " ".join(search_parts)},
        )

    @staticmethod
    def jsonb_contains_query(entity_type, jsonb_filter):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT entity_id, data FROM dynamic_fields_entitydynamicdata WHERE entity_type = %s AND data @> %s::jsonb LIMIT 100",
                [entity_type, json.dumps(jsonb_filter)],
            )
            return [{"entity_id": row[0], "data": row[1]} for row in cursor.fetchall()]

    @staticmethod
    def get_field_statistics(entity_type, field_name):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*), COUNT(DISTINCT value) FROM dynamic_fields_dynamicfieldvalue v JOIN dynamic_fields_dynamicfielddefinition d ON v.definition_id = d.id WHERE d.entity_type = %s AND d.field_name = %s AND v.value IS NOT NULL",
                [entity_type, field_name],
            )
            row = cursor.fetchone()
            return {"total_records": row[0], "unique_values": row[1]}
