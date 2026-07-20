from django.contrib import admin
from .models import ImportJob

@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "file_name", "status", "total_rows", "success_rows", "failed_rows", "created_at"]
    list_filter = ["entity_type", "status", "created_at"]
    search_fields = ["file_name", "created_by__username"]