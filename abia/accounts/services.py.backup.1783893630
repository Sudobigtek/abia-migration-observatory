"""Accounts business logic layer."""
from .repositories import UserRepository, LGARepository
from .exceptions import LGAAccessDenied, UserNotFoundError, LGANotFoundError

class UserService:

    @staticmethod
    def get_by_id(user_id):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        return user
    
    @staticmethod
    def create(data, creator):
        if data.get('role') not in ['admin', 'field_officer', 'supervisor']:
            raise InvalidRoleError("Invalid role specified")
        if data.get('role') == 'field_officer' and data.get('lga_id') != creator.lga_id:
            raise LGAAccessDenied("Cannot assign field officer to different LGA")
        return UserRepository.create(data)
    
    @staticmethod
    def update(user_id, data, updater):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        if updater.role == 'field_officer' and user.lga_id != updater.lga_id:
            raise LGAAccessDenied("Cannot update user outside your LGA")
        return UserRepository.update(user_id, data)
    
    @staticmethod
    def delete(user_id, deleter):
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        if deleter.role == 'field_officer' and user.lga_id != deleter.lga_id:
            raise LGAAccessDenied("Cannot delete user outside your LGA")
        return UserRepository.delete(user_id)
    
    @staticmethod
    def get_users_for_request(request):
        user = request.user
        if user.role == 'field_officer':
            return UserRepository.get_by_lga(user.lga_id)
        return UserRepository.get_all()
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
