import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from abia.migrants.models import Migrant

logger = logging.getLogger("abia.audit")


@receiver(post_save, sender=Migrant)
def log_migrant_save(sender, instance, created, **kwargs):
    action = "CREATED" if created else "UPDATED"
    logger.info(
        "%s migrant_id=%s by_user=%s", action, instance.id, instance.created_by_id
    )


@receiver(post_delete, sender=Migrant)
def log_migrant_delete(sender, instance, **kwargs):
    logger.info("DELETED migrant_id=%s", instance.id)
