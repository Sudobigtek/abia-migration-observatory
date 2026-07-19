import json

from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models

User = get_user_model()


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    INTEGER = "integer", "Integer"
    DECIMAL = "decimal", "Decimal"
    BOOLEAN = "boolean", "Boolean"
    DATE = "date", "Date"
    DATETIME = "datetime", "DateTime"
    CHOICE = "choice", "Single Choice"
    MULTI_CHOICE = "multi_choice", "Multiple Choice"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone Number"
    URL = "url", "URL"
    JSON = "json", "JSON"
    GEOJSON = "geojson", "GeoJSON (Point/Polygon)"
    FILE = "file", "File Upload"
    IMAGE = "image", "Image Upload"


class EntityType(models.TextChoices):
    MIGRANT = "migrant", "Migrant"
    CASE = "case", "Case"
    REFERRAL = "referral", "Referral"
    TRADER = "trader", "Trader"
    SHIPMENT = "shipment", "Shipment"
    CUSTOMS_PROCEDURE = "customs_procedure", "Customs Procedure"


class DynamicFieldDefinition(models.Model):
    entity_type = models.CharField(
        max_length=50, choices=EntityType.choices, db_index=True
    )
    field_name = models.SlugField(max_length=100, db_index=True)
    field_type = models.CharField(
        max_length=20, choices=FieldType.choices, default=FieldType.TEXT
    )
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    choices = models.JSONField(null=True, blank=True)
    default_value = models.JSONField(null=True, blank=True)
    is_required = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=True)
    partner_org = models.CharField(max_length=100, blank=True, db_index=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    validation_regex = models.CharField(max_length=500, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_dynamic_fields",
    )

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by_id:
            from threading import local

            from django.http import HttpRequest

            _thread_locals = local()
            if hasattr(_thread_locals, "request") and hasattr(
                _thread_locals.request, "user"
            ):
                if _thread_locals.request.user.is_authenticated:
                    self.created_by = _thread_locals.request.user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["entity_type", "order", "field_name"]
        unique_together = ["entity_type", "field_name"]
        indexes = [
            models.Index(fields=["entity_type", "is_active"]),
            models.Index(fields=["partner_org", "category"]),
        ]
        verbose_name = "Dynamic Field Definition"
        verbose_name_plural = "Dynamic Field Definitions"

    def clean(self):
        if self.field_type in [FieldType.CHOICE, FieldType.MULTI_CHOICE]:
            if not self.choices or not isinstance(self.choices, list):
                raise DjangoValidationError(
                    "Choice fields must have a non-empty choices list"
                )
        if self.field_type == FieldType.MULTI_CHOICE and self.default_value:
            if not isinstance(self.default_value, list):
                raise DjangoValidationError("Multi-choice default must be a list")

    def __str__(self):
        return f"{self.entity_type}.{self.field_name} ({self.label})"


class DynamicFieldValue(models.Model):
    definition = models.ForeignKey(
        DynamicFieldDefinition, on_delete=models.CASCADE, related_name="values"
    )
    entity_type = models.CharField(max_length=50, db_index=True)
    entity_id = models.PositiveIntegerField(db_index=True)
    value = models.JSONField(null=True, blank=True)
    encrypted_value = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_dynamic_values",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_dynamic_values",
    )

    class Meta:
        unique_together = ["definition", "entity_type", "entity_id"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(
                fields=["entity_type", "entity_id", "definition"],
                name="idx_dynamic_lookup",
            ),
        ]
        verbose_name = "Dynamic Field Value"
        verbose_name_plural = "Dynamic Field Values"

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} -> {self.definition.field_name}"


class EntityDynamicData(models.Model):
    entity_type = models.CharField(max_length=50, db_index=True)
    entity_id = models.PositiveIntegerField(db_index=True)
    data = models.JSONField(default=dict)
    search_vector = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["entity_type", "entity_id"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            GinIndex(
                fields=["data"],
                name="idx_entity_data_gin",
                opclasses=["jsonb_path_ops"],
            ),
        ]
        verbose_name = "Entity Dynamic Data"
        verbose_name_plural = "Entity Dynamic Data"

    def __str__(self):
        field_count = len(self.data) if isinstance(self.data, dict) else 0
        return f"{self.entity_type}:{self.entity_id} ({field_count} fields)"
