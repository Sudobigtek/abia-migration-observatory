from django.contrib import admin
from .models import WebhookEndpoint, WebhookDelivery

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
 list_display = ["name", "url", "event_type", "is_active", "created_at"]
 list_filter = ["event_type", "is_active", "created_at"]
 search_fields = ["name", "url"]

@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
 list_display = ["webhook", "event_type", "status", "attempt_count", "created_at"]
 list_filter = ["status", "event_type", "created_at"]
 search_fields = ["webhook__name", "event_type"]
 readonly_fields = ["response_status", "response_body", "error_message"]