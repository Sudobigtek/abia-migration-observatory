from django.utils import timezone
from .models import Notification, NotificationPreference

class NotificationService:
    @staticmethod
    def send_notification(recipient, title, message, channel="in_app", priority="medium",
                        entity_type="", entity_id="", action_url=""):
        prefs = getattr(recipient, "notification_prefs", None)
        if prefs and not getattr(prefs, f"{channel}_enabled", True):
            return None
        notif = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url
        )
        return notif

    @staticmethod
    def mark_read(notification_id, user):
        from django.shortcuts import get_object_or_404
        notif = get_object_or_404(Notification, id=notification_id, recipient=user)
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save()
        return notif

    @staticmethod
    def get_unread_count(user):
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def broadcast_to_role(role, title, message, priority="medium"):
        from abia.tenant.models import TenantRole
        users = TenantRole.objects.filter(role=role).select_related("user")
        sent = 0
        for tr in users:
            NotificationService.send_notification(tr.user, title, message, priority=priority)
            sent += 1
        return sent