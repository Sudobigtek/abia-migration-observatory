from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PredictionLog

@receiver(post_save, sender=PredictionLog)
def alert_on_failure(sender, instance, created, **kwargs):
    if created and not instance.success:
        pass
