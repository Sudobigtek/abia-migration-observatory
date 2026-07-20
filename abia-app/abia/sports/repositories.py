from django.db.models import Sum, Count, Q
from .models import AthleteProfile, AthleteTransfer

class AthleteRepository:
    @staticmethod
    def get_active():
        return AthleteProfile.objects.filter(is_active=True)

    @staticmethod
    def get_by_sport():
        return list(AthleteProfile.objects.filter(is_active=True).values("sport").annotate(
            athletes=Count("id"),
            abroad=Count("id", filter=Q(transfers__is_international=True))
        ).order_by("-athletes"))

    @staticmethod
    def get_top_valued(limit=20):
        return list(AthleteProfile.objects.filter(is_active=True).exclude(
            market_value_usd=None
        ).order_by("-market_value_usd").values(
            "full_name", "sport", "current_club", "current_country", "market_value_usd"
        )[:limit])

    @staticmethod
    def get_lga_talent_map():
        return list(AthleteProfile.objects.filter(is_active=True).values(
            "origin_lga__name"
        ).annotate(count=Count("id")).order_by("-count"))

class TransferRepository:
    @staticmethod
    def get_completed():
        return AthleteTransfer.objects.filter(status="completed")

    @staticmethod
    def get_international_completed():
        return AthleteTransfer.objects.filter(status="completed", is_international=True)

    @staticmethod
    def get_by_destination():
        return list(TransferRepository.get_completed().values(
            "to_country"
        ).annotate(count=Count("id"), total_fees=Sum("transfer_fee_usd")).order_by("-count"))

    @staticmethod
    def get_talent_export_value():
        total = TransferRepository.get_international_completed().aggregate(
            total=Sum("transfer_fee_usd")
        )["total"] or 0
        count = TransferRepository.get_international_completed().count()
        return {"total_transfer_value_usd": total, "international_transfers": count}