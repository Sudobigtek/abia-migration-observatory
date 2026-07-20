from celery import shared_task
from .services import CBNService

@shared_task
def generate_cbn_summary():
    return CBNService.get_summary()