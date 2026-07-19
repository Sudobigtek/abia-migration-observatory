from django.contrib import admin

from .models import DynamicFieldDefinition, DynamicFieldValue, EntityDynamicData


@admin.register(DynamicFieldDefinition)
class DynamicFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        "field_name",
        "label",
        "entity_type",
        "field_type",
        "partner_org",
        "category",
        "is_active",
        "is_sensitive",
        "order",
    ]
    list_filter = [
        "entity_type",
        "field_type",
        "is_active",
        "is_sensitive",
        "partner_org",
        "category",
    ]
    search_fields = ["field_name", "label", "description"]
    list_editable = ["order", "is_active"]
    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "entity_type",
                    "field_name",
                    "label",
                    "description",
                    "field_type",
                    "order",
                )
            },
        ),
        (
            "Validation",
            {
                "fields": (
                    "is_required",
                    "validation_regex",
                    "min_value",
                    "max_value",
                    "max_length",
                    "choices",
                    "default_value",
                )
            },
        ),
        (
            "Security & Metadata",
            {"fields": ("is_sensitive", "is_searchable",
                        "partner_org", "category")},
        ),
        (
            "Audit",
            {
                "fields": ("is_active", "created_by", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DynamicFieldValue)
class DynamicFieldValueAdmin(admin.ModelAdmin):
    list_display = [
        "definition",
        "entity_type",
        "entity_id",
        "has_value",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["entity_type", "definition__field_type"]
    search_fields = ["entity_id",
                     "definition__field_name", "definition__label"]
    readonly_fields = ("created_at", "updated_at")

    def has_value(self, obj):
        return bool(obj.value or obj.encrypted_value)

    has_value.boolean = True


@admin.register(EntityDynamicData)
class EntityDynamicDataAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "entity_id", "field_count", "updated_at"]
    list_filter = ["entity_type"]
    search_fields = ["entity_id"]
    readonly_fields = ("updated_at",)

    def field_count(self, obj):
        return len(obj.data)

    field_count.short_description = "Fields"
