from django.contrib import admin
from .models import WBIndicator, WBDataPoint, WBConfiguration

@admin.register(WBIndicator)
class WBIndicatorAdmin(admin.ModelAdmin):
    list_display = ["indicator_code", "indicator_name", "category", "unit", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["indicator_code", "indicator_name"]

@admin.register(WBDataPoint)
class WBDataPointAdmin(admin.ModelAdmin):
    list_display = ["indicator", "country_code", "year", "value"]
    list_filter = ["year", "country_code"]
    search_fields = ["indicator__indicator_code", "country_name"]

@admin.register(WBConfiguration)
class WBConfigurationAdmin(admin.ModelAdmin):
    list_display = ["api_base_url", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active"]