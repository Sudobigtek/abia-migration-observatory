import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from abia.cases.models import Case

logger = logging.getLogger("abia.audit")


@receiver(post_save, sender=Case)
def log_case_save(sender, instance, created, **kwargs):
    action = "CREATED" if created else "UPDATED"
    logger.info(
        "%s case_id=%s status=%s by_user=%s",
        action,
        instance.id,
        instance.status,
        instance.created_by_id,
    )


@receiver(post_delete, sender=Case)
def log_case_delete(sender, instance, **kwargs):
    logger.info("DELETED case_id=%s", instance.id)
