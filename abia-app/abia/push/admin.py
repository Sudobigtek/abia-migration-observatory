from django.contrib import admin
from .models import PushDevice, PushNotification

@admin.register(PushDevice)
class PushDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'device_name', 'is_active', 'last_used']
    list_filter = ['platform', 'is_active']

@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'title', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'created_at']
