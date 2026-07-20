from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "recipient", "channel", "priority", "is_read", "created_at"]
    list_filter = ["channel", "priority", "is_read", "created_at"]
    search_fields = ["title", "message", "recipient__username"]

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "email_enabled", "sms_enabled", "push_enabled", "in_app_enabled"]
    list_filter = ["email_enabled", "sms_enabled", "push_enabled"]