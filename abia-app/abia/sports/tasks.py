from celery import shared_task
from .services import SportsService

@shared_task
def generate_sports_export_report():
    return SportsService.get_talent_export_value()