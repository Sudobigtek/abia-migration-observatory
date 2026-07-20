from celery import shared_task
from .services import WTOService

@shared_task
def generate_trade_balance_report():
    return WTOService.get_trade_balance_by_sector()