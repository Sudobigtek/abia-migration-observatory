from rest_framework import serializers
from .models import WebhookEndpoint, WebhookDelivery

class WebhookEndpointSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = WebhookEndpoint
        fields = ["id", "name", "url", "event_type", "secret", "is_active", "retry_count", "timeout_seconds", "headers", "created_by", "created_by_name", "created_at", "updated_at"]

class WebhookDeliverySerializer(serializers.ModelSerializer):
    webhook_name = serializers.CharField(source="webhook.name", read_only=True)
    class Meta:
        model = WebhookDelivery
        fields = ["id", "webhook", "webhook_name", "event_type", "payload", "status", "response_status", "response_body", "attempt_count", "delivered_at", "error_message", "created_at"]