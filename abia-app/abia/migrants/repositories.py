from django.db import transaction

from .models import Migrant


class MigrantRepository:
    @staticmethod
    def get_all():
        return (
            Migrant.objects.select_related("current_lga").order_by("-created_at").all()
        )

    @staticmethod
    def get_by_id(migrant_id):
        return Migrant.objects.filter(id=migrant_id).first()

    @staticmethod
    def get_by_lga(lga_id):
        return Migrant.objects.filter(current_lga_id=lga_id).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create(data):
        return Migrant.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(migrant_id, data):
        Migrant.objects.filter(id=migrant_id).update(**data)
        return Migrant.objects.filter(id=migrant_id).first()

    @staticmethod
    @transaction.atomic
    def delete(migrant_id):
        Migrant.objects.filter(id=migrant_id).delete()

    @staticmethod
    def exists_by_odk_submission_id(odk_id: str) -> bool:
        """Check if an ODK submission has already been processed."""
        if not odk_id:
            return False
        return Migrant.objects.filter(odk_submission_id=odk_id).exists()

    @staticmethod
    def create_from_odk(data: dict) -> Migrant:
        """Create a Migrant record from validated ODK data."""
        return Migrant.objects.create(**data)
