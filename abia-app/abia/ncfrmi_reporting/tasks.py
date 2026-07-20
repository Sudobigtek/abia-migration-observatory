from celery import shared_task
from .services import NCFRMIReportingService
from django.contrib.auth import get_user_model

@shared_task
def generate_monthly_ncfrmi_report(month, year):
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    return NCFRMIReportingService.generate_monthly_report(month, year, user)