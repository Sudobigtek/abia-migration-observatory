
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Beneficiary, PillarParticipation

@receiver(post_save, sender=Beneficiary)
def auto_create_pillar_participations(sender, instance, created, **kwargs):
    """Auto-enroll every new beneficiary in all 4 pillars."""
    if created:
        for pillar_code, _ in PillarParticipation.PILLAR_CHOICES:
            PillarParticipation.objects.get_or_create(
                beneficiary=instance,
                pillar=pillar_code,
                defaults={"enrolled_date": instance.enrolled_date}
            )
