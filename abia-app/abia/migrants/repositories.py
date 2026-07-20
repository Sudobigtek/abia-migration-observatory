from django.db.models import Count
from .models import Migrant

class MigrantRepository:
    @staticmethod
    def count():
        return Migrant.objects.count()

    @staticmethod
    def filter_count(**kwargs):
        return Migrant.objects.filter(**kwargs).count()

    @staticmethod
    def get_lga_breakdown(limit=20):
        return list(Migrant.objects.values("current_lga__name").annotate(
            count=Count("id")
        ).order_by("-count")[:limit])

    @staticmethod
    def get_distinct_lga_count():
        return Migrant.objects.values("current_lga").distinct().count()
