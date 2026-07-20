from celery import shared_task
from .services import ECOWASService

@shared_task
def generate_ecowas_corridor_report():
    return ECOWASService.get_migration_by_corridor()