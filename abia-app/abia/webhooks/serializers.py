from rest_framework import serializers
from .models import WebhookEndpoint, WebhookDelivery

class WebhookEndpointSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'name', 'url', 'events', 'secret', 'is_active', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']

class WebhookDeliverySerializer(serializers.ModelSerializer):
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = ['id', 'endpoint', 'endpoint_name', 'event_type', 'payload', 'response_status', 'status', 'attempts', 'delivered_at', 'created_at']
        read_only_fields = ['id', 'created_at']
