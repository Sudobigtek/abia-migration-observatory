from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationPreference


@shared_task
def send_email_notification(notification_id):
    """Send email notification asynchronously."""
    try:
        notif = Notification.objects.get(id=notification_id)
        pref = NotificationPreference.objects.filter(user=notif.recipient).first()
        
        if pref and not pref.email_enabled:
            return {'status': 'skipped', 'reason': 'email_disabled'}
        
        send_mail(
            subject=notif.title,
            message=notif.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.recipient.email],
            fail_silently=False
        )
        
        import django.utils.timezone
        notif.status = 'sent'
        notif.sent_at = django.utils.timezone.now()
        notif.save()
        return {'status': 'sent', 'notification_id': str(notification_id)}
    except Exception as e:
        notif.status = 'failed'
        notif.save()
        return {'status': 'failed', 'error': str(e)}


@shared_task
def notify_case_critical(case_id, case_title):
    """Notify relevant users when a case is marked critical."""
    from abia.cases.models import Case
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    case = Case.objects.get(id=case_id)
    users = User.objects.filter(role__in=['state_admin', 'super_admin']) | User.objects.filter(id=case.assigned_to_id)
    
    for user in users.distinct():
        notif = Notification.objects.create(
            recipient=user,
            notification_type='case_critical',
            channel='email',
            title=f'CRITICAL: Case #{case_id}',
            message=f'Case "{case_title}" has been marked as CRITICAL priority. Immediate attention required.',
            related_object_type='case',
            related_object_id=case_id
        )
        send_email_notification.delay(str(notif.id))


@shared_task
def notify_referral_status_change(referral_id, old_status, new_status):
    """Notify when referral status changes."""
    from abia.referrals.models import Referral
    ref = Referral.objects.select_related('migrant', 'referred_by').get(id=referral_id)
    
    notif = Notification.objects.create(
        recipient=ref.referred_by,
        notification_type=f'referral_{new_status}',
        channel='in_app',
        title=f'Referral {new_status.title()}',
        message=f'Referral for {ref.migrant.full_name} has been {new_status}.',
        related_object_type='referral',
        related_object_id=referral_id
    )
    if new_status in ['accepted', 'completed']:
        send_email_notification.delay(str(notif.id))


@shared_task
def notify_high_risk(migrant_id, risk_score, risk_level):
    """Alert when a migrant gets a high/critical risk score."""
    from abia.migrants.models import Migrant
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    migrant = Migrant.objects.get(id=migrant_id)
    users = User.objects.filter(role__in=['state_admin', 'super_admin', 'lga_coordinator'])
    
    for user in users.distinct():
        notif = Notification.objects.create(
            recipient=user,
            notification_type=f'risk_{risk_level}',
            channel='email',
            title=f'{risk_level.upper()} RISK: {migrant.full_name}',
            message=f'Migrant {migrant.full_name} has been assessed with {risk_level.upper()} risk (score: {risk_score}). Immediate review required.',
            related_object_type='migrant',
            related_object_id=migrant_id
        )
        send_email_notification.delay(str(notif.id))


@shared_task
def send_daily_digest():
    """Send daily summary of pending items to users."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    for pref in NotificationPreference.objects.filter(daily_digest=True, email_enabled=True):
        pending_notifs = Notification.objects.filter(
            recipient=pref.user, status__in=['pending', 'sent'], created_at__date=__import__('django.utils.timezone').utils.timezone.now().date()
        )
        if pending_notifs.exists():
            summary = "\n".join([f"- {n.title}" for n in pending_notifs[:10]])
            send_mail(
                subject='Daily Digest - Abia Migration Observatory',
                message=f'Your pending notifications for today:\n\n{summary}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[pref.user.email],
                fail_silently=True
            )
