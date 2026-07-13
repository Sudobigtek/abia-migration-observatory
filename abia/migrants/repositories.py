"""Migrants data access layer."""
from django.db import transaction
from .models import Migrant

class MigrantRepository:
    @staticmethod
    def get_all():
        return list(Migrant.objects.select_related("current_lga").all())

    @staticmethod
    def get_by_lga(lga_id):
        return list(Migrant.objects.filter(current_lga_id=lga_id).select_related("current_lga"))

    @staticmethod
    def get_by_id(migrant_id):
        try:
            return Migrant.objects.select_related("current_lga").get(id=migrant_id)
        except Migrant.DoesNotExist:
            return None

    @staticmethod
    def exists_by_odk_id(odk_id):
        return Migrant.objects.filter(odk_submission_id=odk_id).exists()

    @staticmethod
    @transaction.atomic
    def create(data):
        return Migrant.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(migrant_id, data):
        Migrant.objects.filter(id=migrant_id).update(**data)
        return MigrantRepository.get_by_id(migrant_id)

    @staticmethod
    @transaction.atomic
    def delete(migrant_id):
        Migrant.objects.filter(id=migrant_id).delete()
