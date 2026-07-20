from celery import shared_task
from .services import WorldBankService

@shared_task
def fetch_wb_migration_indicators():
    return WorldBankService.get_migration_indicators()