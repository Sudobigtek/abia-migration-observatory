"""Accounts data access layer."""
from django.db import transaction
from .models import User, LGA

class UserRepository:
    @staticmethod
    def get_all():
        return list(User.objects.select_related("lga").all())

    @staticmethod
    def get_by_lga(lga_id):
        return list(User.objects.filter(lga_id=lga_id).select_related("lga"))

    @staticmethod
    def get_by_id(user_id):
        try:
            return User.objects.select_related("lga").get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create(data):
        return User.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(user_id, data):
        User.objects.filter(id=user_id).update(**data)
        return UserRepository.get_by_id(user_id)

    @staticmethod
    @transaction.atomic
    def delete(user_id):
        User.objects.filter(id=user_id).delete()

class LGARepository:
    @staticmethod
    def get_all():
        return list(LGA.objects.all())

    @staticmethod
    def get_by_id(lga_id):
        try:
            return LGA.objects.get(id=lga_id)
        except LGA.DoesNotExist:
            return None
