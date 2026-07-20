from .models import Case

class CaseRepository:
    @staticmethod
    def count():
        return Case.objects.count()

    @staticmethod
    def filter_count(**kwargs):
        return Case.objects.filter(**kwargs).count()