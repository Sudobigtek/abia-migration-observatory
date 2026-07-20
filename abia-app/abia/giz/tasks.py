from celery import shared_task
from .services import GIZService

@shared_task
def refresh_giz_indicators():
    return GIZService.update_indicators_from_data()

@shared_task
def generate_giz_migration_report():
    return GIZService.build_migration_governance_report()