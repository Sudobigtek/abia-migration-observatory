from django.contrib import admin
from .models import BackupJob, RestoreJob

@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    list_display = ["backup_type", "status", "file_size", "row_count", "created_by", "created_at"]
    list_filter = ["backup_type", "status", "created_at"]
    search_fields = ["file_path", "created_by__username"]

@admin.register(RestoreJob)
class RestoreJobAdmin(admin.ModelAdmin):
    list_display = ["backup", "status", "row_count", "created_by", "created_at"]
    list_filter = ["status", "created_at"]