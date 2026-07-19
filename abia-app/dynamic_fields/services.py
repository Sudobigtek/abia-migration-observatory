import json
import re
from typing import Any, Dict, List, Optional

from django.db import transaction

from .exceptions import DuplicateFieldError, FieldTypeError, ValidationError
from .models import (
    DynamicFieldDefinition,
    DynamicFieldValue,
    EntityDynamicData,
    EntityType,
    FieldType,
)


class FieldValidationService:
    @staticmethod
    def validate(definition, value):
        if value is None and definition.is_required:
            raise ValidationError(f"{definition.field_name} is required")
        if value is None:
            return None
        validators = {
            FieldType.TEXT: FieldValidationService._validate_text,
            FieldType.NUMBER: FieldValidationService._validate_number,
            FieldType.INTEGER: FieldValidationService._validate_integer,
            FieldType.DECIMAL: FieldValidationService._validate_decimal,
            FieldType.BOOLEAN: FieldValidationService._validate_boolean,
            FieldType.DATE: FieldValidationService._validate_date,
            FieldType.DATETIME: FieldValidationService._validate_datetime,
            FieldType.CHOICE: FieldValidationService._validate_choice,
            FieldType.MULTI_CHOICE: FieldValidationService._validate_multi_choice,
            FieldType.EMAIL: FieldValidationService._validate_email,
            FieldType.PHONE: FieldValidationService._validate_phone,
            FieldType.URL: FieldValidationService._validate_url,
            FieldType.JSON: FieldValidationService._validate_json,
            FieldType.GEOJSON: FieldValidationService._validate_geojson,
            FieldType.FILE: FieldValidationService._validate_file,
            FieldType.IMAGE: FieldValidationService._validate_image,
        }
        validator = validators.get(definition.field_type)
        if not validator:
            raise FieldTypeError(f"Unknown field type: {definition.field_type}")
        return validator(definition, value)

    @staticmethod
    def _validate_text(defn, value):
        if not isinstance(value, str):
            raise ValidationError("Expected string")
        if defn.max_length and len(value) > defn.max_length:
            raise ValidationError(f"Max length {defn.max_length} exceeded")
        if defn.validation_regex and not re.match(defn.validation_regex, value):
            raise ValidationError("Value does not match required pattern")
        return value

    @staticmethod
    def _validate_number(defn, value):
        try:
            num = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Expected number")
        if defn.min_value is not None and num < defn.min_value:
            raise ValidationError(f"Minimum value: {defn.min_value}")
        if defn.max_value is not None and num > defn.max_value:
            raise ValidationError(f"Maximum value: {defn.max_value}")
        return num

    @staticmethod
    def _validate_integer(defn, value):
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Expected integer")
        if defn.min_value is not None and num < defn.min_value:
            raise ValidationError(f"Minimum value: {defn.min_value}")
        if defn.max_value is not None and num > defn.max_value:
            raise ValidationError(f"Maximum value: {defn.max_value}")
        return num

    @staticmethod
    def _validate_decimal(defn, value):
        return FieldValidationService._validate_number(defn, value)

    @staticmethod
    def _validate_boolean(defn, value):
        if isinstance(value, bool):
            return value
        if value in (1, "1", "true", "True", "yes"):
            return True
        if value in (0, "0", "false", "False", "no"):
            return False
        raise ValidationError("Expected boolean")

    @staticmethod
    def _validate_date(defn, value):
        from datetime import datetime

        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError("Expected YYYY-MM-DD")
        return value

    @staticmethod
    def _validate_datetime(defn, value):
        from datetime import datetime

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError("Expected ISO datetime")
        return value

    @staticmethod
    def _validate_choice(defn, value):
        if value not in defn.choices:
            raise ValidationError(f"Choice must be one of: {defn.choices}")
        return value

    @staticmethod
    def _validate_multi_choice(defn, value):
        if not isinstance(value, list):
            raise ValidationError("Expected list of choices")
        invalid = [v for v in value if v not in defn.choices]
        if invalid:
            raise ValidationError(f"Invalid choices: {invalid}")
        return value

    @staticmethod
    def _validate_email(defn, value):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, str(value)):
            raise ValidationError("Invalid email format")
        return value

    @staticmethod
    def _validate_phone(defn, value):
        cleaned = re.sub(r"[^\d+]", "", str(value))
        if len(cleaned) < 7:
            raise ValidationError("Phone number too short")
        return cleaned

    @staticmethod
    def _validate_url(defn, value):
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(pattern, str(value), re.IGNORECASE):
            raise ValidationError("Invalid URL format")
        return value

    @staticmethod
    def _validate_json(defn, value):
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            raise ValidationError("Invalid JSON")

    @staticmethod
    def _validate_geojson(defn, value):
        if not isinstance(value, dict):
            raise ValidationError("GeoJSON must be a dict")
        if value.get("type") not in ("Point", "Polygon", "LineString", "MultiPoint"):
            raise ValidationError("Invalid GeoJSON type")
        if "coordinates" not in value:
            raise ValidationError("GeoJSON missing coordinates")
        return value

    @staticmethod
    def _validate_file(defn, value):
        if not isinstance(value, str):
            raise ValidationError("File value must be URL string")
        return value

    @staticmethod
    def _validate_image(defn, value):
        return FieldValidationService._validate_file(defn, value)


class DynamicFieldService:
    @staticmethod
    def create_field_definition(data, user):
        entity_type = data.get("entity_type")
        field_name = data.get("field_name")
        if DynamicFieldDefinition.objects.filter(
            entity_type=entity_type, field_name=field_name
        ).exists():
            raise DuplicateFieldError(
                f"Field {field_name} already exists for {entity_type}"
            )
        definition = DynamicFieldDefinition.objects.create(created_by=user, **data)
        return definition

    @staticmethod
    def set_field_value(definition, entity_type, entity_id, value, user):
        validated = FieldValidationService.validate(definition, value)
        with transaction.atomic():
            obj, created = DynamicFieldValue.objects.update_or_create(
                definition=definition,
                entity_type=entity_type,
                entity_id=entity_id,
                defaults={
                    "value": validated if not definition.is_sensitive else None,
                    "updated_by": user,
                    "created_by": user,
                },
            )
            if definition.is_sensitive and validated is not None:
                import base64

                from cryptography.fernet import Fernet
                from django.conf import settings

                key = settings.DYNAMIC_FIELD_ENCRYPTION_KEY.encode()
                f = Fernet(base64.urlsafe_b64encode(key[:32].ljust(32, b"0")))
                obj.encrypted_value = f.encrypt(json.dumps(validated).encode())
                obj.save(update_fields=["encrypted_value"])
        return obj

    @staticmethod
    def get_entity_dynamic_data(entity_type, entity_id):
        try:
            aggregate = EntityDynamicData.objects.get(
                entity_type=entity_type, entity_id=entity_id
            )
            return aggregate.data
        except EntityDynamicData.DoesNotExist:
            return {}

    @staticmethod
    def get_fields_for_entity_type(entity_type, active_only=True):
        qs = DynamicFieldDefinition.objects.filter(entity_type=entity_type)
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs.order_by("order", "field_name"))

    @staticmethod
    def delete_field_value(definition, entity_type, entity_id, user):
        DynamicFieldValue.objects.filter(
            definition=definition, entity_type=entity_type, entity_id=entity_id
        ).delete()

    @staticmethod
    def search_entities(entity_type, query, filters=None):
        from django.db.models import Q

        qs = EntityDynamicData.objects.filter(entity_type=entity_type)
        if query:
            qs = qs.filter(Q(search_vector__icontains=query) | Q(data__icontains=query))
        if filters:
            for key, val in filters.items():
                qs = qs.filter(data__contains={key: val})
        return [{"entity_id": e.entity_id, "data": e.data} for e in qs[:100]]


class ODKFormGenerationService:
    @staticmethod
    def generate_xlsform_questions(entity_type):
        fields = DynamicFieldService.get_fields_for_entity_type(entity_type)
        questions = []
        for f in fields:
            q = ODKFormGenerationService._map_to_odk(f)
            questions.append(q)
        return questions

    @staticmethod
    def _map_to_odk(defn):
        type_map = {
            FieldType.TEXT: "text",
            FieldType.NUMBER: "decimal",
            FieldType.INTEGER: "integer",
            FieldType.DECIMAL: "decimal",
            FieldType.BOOLEAN: "select_one yes_no",
            FieldType.DATE: "date",
            FieldType.DATETIME: "dateTime",
            FieldType.CHOICE: "select_one",
            FieldType.MULTI_CHOICE: "select_multiple",
            FieldType.EMAIL: "text",
            FieldType.PHONE: "text",
            FieldType.URL: "text",
            FieldType.JSON: "text",
            FieldType.GEOJSON: "geopoint",
            FieldType.FILE: "file",
            FieldType.IMAGE: "image",
        }
        q = {
            "type": type_map.get(defn.field_type, "text"),
            "name": defn.field_name,
            "label": defn.label,
            "hint": defn.description,
            "required": "yes" if defn.is_required else "no",
        }
        if defn.field_type in [FieldType.CHOICE, FieldType.MULTI_CHOICE]:
            choices = " ".join(defn.choices) if defn.choices else ""
            q["type"] += f" {choices}"
        if defn.validation_regex:
            q["constraint"] = f'regex(., "{defn.validation_regex}")'
        return q
