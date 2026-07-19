from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name', 'notification_type', 'channel',
            'title', 'message', 'related_object_type', 'related_object_id',
            'status', 'sent_at', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_enabled', 'sms_enabled', 'push_enabled',
            'case_critical_email', 'case_critical_sms',
            'referral_updates_email', 'risk_alerts_email', 'risk_alerts_sms',
            'daily_digest', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
