from django.contrib import admin
from .models import IOMDataExchange, IOMConfiguration

@admin.register(IOMDataExchange)
class IOMDataExchangeAdmin(admin.ModelAdmin):
    list_display = ["direction", "entity_type", "status", "iom_reference", "created_at"]
    list_filter = ["direction", "entity_type", "status", "created_at"]
    search_fields = ["iom_reference", "entity_id"]

@admin.register(IOMConfiguration)
class IOMConfigurationAdmin(admin.ModelAdmin):
    list_display = ["api_base_url", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active", "auto_sync_enabled"]