from django.db import transaction

from .models import LGA, User


class LGARepository:
    @staticmethod
    def get_all():
        return LGA.objects.order_by("name").all()

    @staticmethod
    def get_by_id(lga_id):
        return LGA.objects.filter(id=lga_id).first()

    @staticmethod
    def get_by_code(code):
        return LGA.objects.filter(code=code).first()


class UserRepository:
    @staticmethod
    def get_all():
        return User.objects.select_related("lga").order_by("id").all()

    @staticmethod
    def get_by_id(user_id):
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def get_by_lga(lga_id):
        return User.objects.filter(lga_id=lga_id).order_by("id")

    @staticmethod
    def get_by_username(username):
        return User.objects.filter(username=username).first()

    @staticmethod
    @transaction.atomic
    def create(data):
        return User.objects.create_user(**data)

    @staticmethod
    @transaction.atomic
    def update(user_id, data):
        User.objects.filter(id=user_id).update(**data)
        return User.objects.filter(id=user_id).first()

    @staticmethod
    @transaction.atomic
    def delete(user_id):
        User.objects.filter(id=user_id).delete()

    @staticmethod
    @transaction.atomic
    def create_superuser(data):
        return User.objects.create_superuser(**data)
