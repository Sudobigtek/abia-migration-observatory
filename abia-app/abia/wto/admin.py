from django.contrib import admin
from .models import TradeRecord, WTOConfiguration

@admin.register(TradeRecord)
class TradeRecordAdmin(admin.ModelAdmin):
    list_display = ["flow_type", "product_category", "sector", "value_usd", "trade_partner", "year", "quarter"]
    list_filter = ["flow_type", "sector", "year", "quarter"]
    search_fields = ["product_category", "hs_code", "trade_partner"]

@admin.register(WTOConfiguration)
class WTOConfigurationAdmin(admin.ModelAdmin):
    list_display = ["api_base_url", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active"]