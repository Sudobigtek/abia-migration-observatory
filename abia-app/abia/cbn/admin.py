from django.contrib import admin
from .models import RemittanceRecord, CBNConfiguration

@admin.register(RemittanceRecord)
class RemittanceRecordAdmin(admin.ModelAdmin):
    list_display = ["sender_name", "recipient_name", "naira_equivalent", "channel", "recipient_lga", "transaction_date", "status"]
    list_filter = ["channel", "purpose", "status", "verified_by_cbn", "transaction_date"]
    search_fields = ["sender_name", "recipient_name", "transaction_reference", "cbn_reference"]

@admin.register(CBNConfiguration)
class CBNConfigurationAdmin(admin.ModelAdmin):
    list_display = ["api_base_url", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active", "auto_sync_enabled"]