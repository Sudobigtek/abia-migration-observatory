from django.contrib import admin
from .models import AthleteProfile, AthleteTransfer, SportsConfiguration

@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "sport", "position", "current_club", "current_country", "market_value_usd", "origin_lga", "is_active"]
    list_filter = ["sport", "gender", "nationality", "is_active"]
    search_fields = ["full_name", "current_club", "position"]

@admin.register(AthleteTransfer)
class AthleteTransferAdmin(admin.ModelAdmin):
    list_display = ["athlete", "from_club", "to_club", "to_country", "transfer_fee_usd", "transfer_date", "status", "is_international"]
    list_filter = ["transfer_type", "status", "is_international", "transfer_date"]
    search_fields = ["athlete__full_name", "from_club", "to_club", "agent_name"]

@admin.register(SportsConfiguration)
class SportsConfigurationAdmin(admin.ModelAdmin):
    list_display = ["data_source_name", "is_active", "auto_sync_enabled", "last_sync_at"]
    list_filter = ["is_active"]