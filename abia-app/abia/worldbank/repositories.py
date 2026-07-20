from .models import WBDataPoint, WBIndicator

class WBIndicatorRepository:
    @staticmethod
    def get_active():
        return WBIndicator.objects.filter(is_active=True)

    @staticmethod
    def get_by_category(category):
        qs = WBIndicator.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        return qs

    @staticmethod
    def get_indicator_trend(indicator_code, country_code="NGA"):
        return list(WBDataPoint.objects.filter(
            indicator__indicator_code=indicator_code, country_code=country_code
        ).values("year", "value").order_by("year"))

    @staticmethod
    def get_latest_for_indicator(indicator):
        return indicator.data_points.order_by("-year").first()
