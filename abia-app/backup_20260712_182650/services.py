from .repositories import UserRepository, LGARepository
from abia.common.exceptions import LGAAccessDenied, UserNotFoundError, LGANotFoundError


class UserService:
    @staticmethod
    def get_users_for_request(request):
        user = request.user
        if user.role in ("state_admin", "super_admin"):
            return UserRepository.get_all()
        return UserRepository.get_by_lga(user.lga_id)

    @staticmethod
    def create_user(data, creator):
        if creator.role == "field_officer" and data.get("lga") != creator.lga:
            raise LGAAccessDenied("Cannot create user outside your LGA")
        return UserRepository.create(data)

    @staticmethod
    def get_user_by_id(user_id, requester):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if requester.role not in ("state_admin", "super_admin"):
            if user.lga != requester.lga:
                raise LGAAccessDenied()
        return user


class LGAService:
    @staticmethod
    def get_all_lgas():
        return LGARepository.get_all()

    @staticmethod
    def get_lga_by_id(lga_id):
        lga = LGARepository.get_by_id(lga_id)
        if not lga:
            raise LGANotFoundError()
        return lga
