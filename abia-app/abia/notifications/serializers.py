from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source="recipient.get_full_name", read_only=True)
    class Meta:
        model = Notification
        fields = ["id", "recipient", "recipient_name", "title", "message", "channel",
                  "priority", "entity_type", "entity_id", "is_read", "read_at",
                  "action_url", "created_at"]

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ["id", "email_enabled", "sms_enabled", "push_enabled", "in_app_enabled",
                  "quiet_hours_start", "quiet_hours_end"]