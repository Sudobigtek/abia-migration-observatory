"""Cases data access layer."""
from django.db import transaction
from .models import Case

class CaseRepository:
    @staticmethod
    def get_all():
        return list(Case.objects.select_related("lga", "created_by").all())

    @staticmethod
    def get_by_lga(lga_id):
        return list(Case.objects.filter(lga_id=lga_id).select_related("lga", "created_by"))

    @staticmethod
    def get_by_id(case_id):
        try:
            return Case.objects.select_related("lga", "created_by").get(id=case_id)
        except Case.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create(data):
        return Case.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(case_id, data):
        Case.objects.filter(id=case_id).update(**data)
        return CaseRepository.get_by_id(case_id)

    @staticmethod
    @transaction.atomic
    def delete(case_id):
        Case.objects.filter(id=case_id).delete()
