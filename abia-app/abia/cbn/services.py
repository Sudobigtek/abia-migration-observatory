from django.db.models import Sum, Count, Avg
from .models import RemittanceRecord

class CBNService:
    @staticmethod
    def get_summary():
        return RemittanceRecord.objects.filter(status="completed").aggregate(
            total_naira=Sum("naira_equivalent"),
            total_count=Count("id"),
            avg_amount=Avg("naira_equivalent"),
        )

    @staticmethod
    def get_by_lga():
        data = RemittanceRecord.objects.filter(status="completed").values(
            "recipient_lga__name"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total")[:20]
        return list(data)

    @staticmethod
    def get_by_channel():
        data = RemittanceRecord.objects.filter(status="completed").values(
            "channel"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total")
        return list(data)

    @staticmethod
    def get_by_purpose():
        data = RemittanceRecord.objects.filter(status="completed").values(
            "purpose"
        ).annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("-total")
        return list(data)

    @staticmethod
    def get_monthly_trends():
        from django.db.models.functions import TruncMonth
        data = RemittanceRecord.objects.filter(status="completed").annotate(
            month=TruncMonth("transaction_date")
        ).values("month").annotate(total=Sum("naira_equivalent"), count=Count("id")).order_by("month")
        return list(data)