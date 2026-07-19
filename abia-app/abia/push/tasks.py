from celery import shared_task
from .models import PushDevice, PushNotification

@shared_task
def send_push_notification(user_id, title, body, data=None):
    """Send push notification to all active devices for a user."""
    devices = PushDevice.objects.filter(user_id=user_id, is_active=True)
    
    if not devices.exists():
        return {'status': 'no_devices'}

    # Placeholder: Integrate with Firebase Cloud Messaging
    # from firebase_admin import messaging
    # for device in devices:
    #     message = messaging.Message(
    #         notification=messaging.Notification(title=title, body=body),
    #         data=data or {},
    #         token=device.device_token,
    #     )
    #     messaging.send(message)

    # For now, create notification records
    for device in devices:
        PushNotification.objects.create(
            recipient_id=user_id,
            title=title,
            body=body,
            data=data or {},
            status='sent',
            sent_at=__import__('django.utils.timezone').utils.timezone.now()
        )

    return {'status': 'sent', 'device_count': devices.count()}

@shared_task
def broadcast_push_notification(title, body, data=None, role_filter=None):
    """Broadcast to all users or filtered by role."""
    from abia.accounts.models import User
    users = User.objects.all()
    if role_filter:
        users = users.filter(role__in=role_filter)
    
    sent = 0
    for user in users:
        result = send_push_notification.delay(user.id, title, body, data)
        sent += 1
    
    return {'status': 'broadcasting', 'target_users': sent}
