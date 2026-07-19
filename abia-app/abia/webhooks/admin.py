from django.contrib import admin
from .models import WebhookEndpoint, WebhookDelivery

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'url']

@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'event_type', 'status', 'attempts', 'created_at']
    list_filter = ['status', 'event_type', 'created_at']
