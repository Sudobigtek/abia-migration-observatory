from django.db import transaction

from .models import Case


class CaseRepository:
    @staticmethod
    def get_all():
        return (
            Case.objects.select_related("migrant", "lga").order_by("-created_at").all()
        )

    @staticmethod
    def get_by_id(case_id):
        return Case.objects.filter(id=case_id).first()

    @staticmethod
    def get_by_lga(lga_id):
        return Case.objects.filter(lga_id=lga_id).order_by("-created_at")

    @staticmethod
    def get_by_migrant(migrant_id):
        return Case.objects.filter(migrant_id=migrant_id)

    @staticmethod
    @transaction.atomic
    def create(data):
        return Case.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(case_id, data):
        Case.objects.filter(id=case_id).update(**data)
        return Case.objects.filter(id=case_id).first()

    @staticmethod
    @transaction.atomic
    def delete(case_id):
        Case.objects.filter(id=case_id).delete()
