"""Referrals data access layer."""
from django.db import transaction
from .models import Referral

class ReferralRepository:
    @staticmethod
    def get_all():
        return list(Referral.objects.select_related("from_lga", "to_lga", "created_by").all())

    @staticmethod
    def get_by_lga(lga_id):
        return list(Referral.objects.filter(from_lga_id=lga_id).select_related("from_lga", "to_lga", "created_by"))

    @staticmethod
    def get_by_id(referral_id):
        try:
            return Referral.objects.select_related("from_lga", "to_lga", "created_by").get(id=referral_id)
        except Referral.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create(data):
        return Referral.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(referral_id, data):
        Referral.objects.filter(id=referral_id).update(**data)
        return ReferralRepository.get_by_id(referral_id)

    @staticmethod
    @transaction.atomic
    def delete(referral_id):
        Referral.objects.filter(id=referral_id).delete()
