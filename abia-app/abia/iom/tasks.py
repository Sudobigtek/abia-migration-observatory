from celery import shared_task
from .services import IOMService

@shared_task
def sync_all_migrants_to_iom():
    return IOMService.sync_all_to_iom("migrant")

@shared_task
def sync_all_cases_to_iom():
    return IOMService.sync_all_to_iom("case")