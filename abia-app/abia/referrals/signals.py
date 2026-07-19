import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from abia.referrals.models import Referral

logger = logging.getLogger("abia.audit")


@receiver(post_save, sender=Referral)
def log_referral_save(sender, instance, created, **kwargs):
    action = "CREATED" if created else "UPDATED"
    logger.info(
        "%s referral_id=%s status=%s from_lga=%s to_lga=%s",
        action,
        instance.id,
        instance.status,
        instance.from_lga_id,
        instance.to_lga_id,
    )


@receiver(post_delete, sender=Referral)
def log_referral_delete(sender, instance, **kwargs):
    logger.info("DELETED referral_id=%s", instance.id)
