from django.contrib import admin
from .models import GIZDataExchange, GIZIndicator

@admin.register(GIZDataExchange)
class GIZDataExchangeAdmin(admin.ModelAdmin):
    list_display = ["title", "programme_area", "status", "giz_project_code", "created_by", "created_at"]
    list_filter = ["programme_area", "status", "created_at"]
    search_fields = ["title", "giz_project_code"]

@admin.register(GIZIndicator)
class GIZIndicatorAdmin(admin.ModelAdmin):
    list_display = ["name", "programme_area", "current_value", "target_value", "progress_percentage", "is_active"]
    list_filter = ["programme_area", "is_active"]
    search_fields = ["name", "category"]