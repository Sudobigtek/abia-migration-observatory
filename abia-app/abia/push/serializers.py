from rest_framework import serializers
from .models import PushDevice, PushNotification

class PushDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushDevice
        fields = ['id', 'platform', 'device_token', 'device_name', 'is_active', 'last_used', 'created_at']
        read_only_fields = ['id', 'last_used', 'created_at']

class PushNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotification
        fields = ['id', 'recipient', 'title', 'body', 'data', 'status', 'sent_at', 'delivered_at', 'created_at']
        read_only_fields = ['id', 'sent_at', 'delivered_at', 'created_at']
