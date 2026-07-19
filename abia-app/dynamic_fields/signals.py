from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import DynamicFieldValue
from .repositories import DynamicFieldRepository


@receiver(post_save, sender=DynamicFieldValue)
def rebuild_aggregate_on_save(sender, instance, **kwargs):
    DynamicFieldRepository.rebuild_aggregate(instance.entity_type, instance.entity_id)


@receiver(post_delete, sender=DynamicFieldValue)
def rebuild_aggregate_on_delete(sender, instance, **kwargs):
    DynamicFieldRepository.rebuild_aggregate(instance.entity_type, instance.entity_id)
