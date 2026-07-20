from django.contrib import admin
from .models import ECOWASMigrantFlow, ECOWASTradeFlow, ECOWASConfiguration

@admin.register(ECOWASMigrantFlow)
class ECOWASMigrantFlowAdmin(admin.ModelAdmin):
    list_display = ["country_of_origin", "country_of_destination", "migration_type", "sector", "estimated_count", "year"]
    list_filter = ["migration_type", "gender", "year", "sector"]
    search_fields = ["country_of_origin", "country_of_destination", "protocol_article"]

@admin.register(ECOWASTradeFlow)
class ECOWASTradeFlowAdmin(admin.ModelAdmin):
    list_display = ["reporter_country", "partner_country", "product_category", "export_value", "import_value", "year"]
    list_filter = ["year", "reporter_country"]
    search_fields = ["partner_country", "product_category"]

@admin.register(ECOWASConfiguration)
class ECOWASConfigurationAdmin(admin.ModelAdmin):
    list_display = ["api_base_url", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active"]