from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'channel', 'status', 'created_at']
    list_filter = ['status', 'channel', 'notification_type', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['id', 'created_at', 'sent_at', 'read_at']
    date_hierarchy = 'created_at'

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'daily_digest']
    list_filter = ['email_enabled', 'sms_enabled', 'daily_digest']
