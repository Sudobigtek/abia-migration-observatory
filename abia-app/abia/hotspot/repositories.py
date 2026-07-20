from .models import HotspotPrediction

class HotspotRepository:
    @staticmethod
    def filter_count(**kwargs):
        return HotspotPrediction.objects.filter(**kwargs).count()