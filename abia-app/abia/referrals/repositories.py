from .models import Referral

class ReferralRepository:
    @staticmethod
    def count():
        return Referral.objects.count()

    @staticmethod
    def filter_count(**kwargs):
        return Referral.objects.filter(**kwargs).count()
