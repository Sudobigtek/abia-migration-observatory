from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from .models import RemittanceRecord

class RemittanceRepository:
    @staticmethod
    def get_completed():
        return RemittanceRecord.objects.filter(status="completed")

    @staticmethod
    def get_summary():
        return RemittanceRepository.get_completed().aggregate(
            total_naira=Sum("naira_equivalent"),
            total_count=Count("id"),
            avg_amount=Avg("naira_equivalent"),
        )

    @staticmethod
    def get_by_lga():
        return list(RemittanceRepository.get_completed().values(
            "recipient_lga__name"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total")[:20])

    @staticmethod
    def get_by_channel():
        return list(RemittanceRepository.get_completed().values(
            "channel"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total"))

    @staticmethod
    def get_by_purpose():
        return list(RemittanceRepository.get_completed().values(
            "purpose"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total"))

    @staticmethod
    def get_monthly_trends():
        return list(RemittanceRepository.get_completed().annotate(
            month=TruncMonth("transaction_date")
        ).values("month").annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("month"))
