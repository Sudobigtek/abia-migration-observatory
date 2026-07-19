from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import notify_case_critical, notify_referral_status_change, notify_high_risk
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.ai.models import RiskAssessment


@receiver(post_save, sender=Case)
def case_notification(sender, instance, created, **kwargs):
    if instance.priority == 'critical' and (created or instance.tracker.has_changed('priority')):
        notify_case_critical.delay(str(instance.id), instance.title)


@receiver(post_save, sender=Referral)
def referral_notification(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        notify_referral_status_change.delay(str(instance.id), old_status, instance.status)


@receiver(post_save, sender=RiskAssessment)
def risk_notification(sender, instance, created, **kwargs):
    if created and instance.risk_level in ['high', 'critical']:
        notify_high_risk.delay(str(instance.migrant.id), instance.risk_score, instance.risk_level)
