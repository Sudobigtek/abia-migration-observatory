from django.db.models import Sum, Count, Q
from .models import AthleteProfile, AthleteTransfer

class SportsService:
    @staticmethod
    def get_transfers_by_destination():
        data = AthleteTransfer.objects.filter(status="completed").values(
            "to_country"
        ).annotate(count=Count("id"), total_fees=Sum("transfer_fee_usd")).order_by("-count")
        return list(data)

    @staticmethod
    def get_talent_export_value():
        total = AthleteTransfer.objects.filter(
            status="completed", is_international=True
        ).aggregate(total=Sum("transfer_fee_usd"))["total"] or 0
        count = AthleteTransfer.objects.filter(status="completed", is_international=True).count()
        return {"total_transfer_value_usd": total, "international_transfers": count}

    @staticmethod
    def get_by_sport():
        data = AthleteProfile.objects.filter(is_active=True).values("sport").annotate(
            athletes=Count("id"),
            abroad=Count("id", filter=Q(transfers__is_international=True))
        ).order_by("-athletes")
        return list(data)

    @staticmethod
    def get_top_valued_athletes(limit=20):
        return list(AthleteProfile.objects.filter(is_active=True).exclude(
            market_value_usd=None
        ).order_by("-market_value_usd").values("full_name", "sport", "current_club", "current_country", "market_value_usd")[:limit])

    @staticmethod
    def get_lga_talent_map():
        data = AthleteProfile.objects.filter(is_active=True).values(
            "origin_lga__name"
        ).annotate(count=Count("id")).order_by("-count")
        return list(data)