from django.contrib import admin
from .models import ChartDashboard

@admin.register(ChartDashboard)
class ChartDashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "chart_type", "data_source", "is_public", "created_by", "created_at"]
    list_filter = ["chart_type", "data_source", "is_public", "created_at"]
    search_fields = ["name", "data_source"]