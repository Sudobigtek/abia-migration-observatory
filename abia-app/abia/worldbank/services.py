from django.db.models import Avg
from .models import WBDataPoint, WBIndicator

class WorldBankService:
    @staticmethod
    def get_indicator_trend(indicator_code, country_code="NGA"):
        points = WBDataPoint.objects.filter(
            indicator__indicator_code=indicator_code, country_code=country_code
        ).values("year", "value").order_by("year")
        return list(points)

    @staticmethod
    def get_latest_values(category=None):
        qs = WBIndicator.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        results = []
        for ind in qs:
            latest = ind.data_points.order_by("-year").first()
            if latest:
                results.append({
                    "indicator_code": ind.indicator_code,
                    "indicator_name": ind.indicator_name,
                    "year": latest.year,
                    "value": latest.value,
                    "unit": ind.unit,
                })
        return results

    @staticmethod
    def get_migration_indicators():
        return WorldBankService.get_latest_values(category="migration")

    @staticmethod
    def get_remittance_indicators():
        return WorldBankService.get_latest_values(category="remittance")