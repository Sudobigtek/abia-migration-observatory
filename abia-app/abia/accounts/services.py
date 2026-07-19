from typing import Any

from common.exceptions import (
    InvalidRoleError,
    LGAAccessDenied,
    LGANotFoundError,
    UserNotFoundError,
)

from .repositories import LGARepository, UserRepository

VALID_ROLES = {"field_officer", "lga_coordinator", "state_admin", "super_admin"}


class UserService:
    """Business logic for user operations."""

    @staticmethod
    def _get_lga_id(lga_obj: Any) -> Any:
        """Extract an LGA ID from an object or return the raw ID."""
        return lga_obj.id if hasattr(lga_obj, "id") else lga_obj

    @staticmethod
    def get_users_for_request(request: Any) -> Any:
        """Return users visible to the requesting user."""
        user = request.user
        role = getattr(user, "role", None)
        if role in ("state_admin", "super_admin"):
            return UserRepository.get_all()
        lga = getattr(user, "lga", None)
        lga_id = lga.id if lga and hasattr(lga, "id") else getattr(user, "lga_id", None)
        return UserRepository.get_by_lga(lga_id)

    @staticmethod
    def create(data: dict, creator: Any) -> Any:
        """Create a user with role validation and LGA access control."""
        role = data.get("role")
        if role not in VALID_ROLES:
            raise InvalidRoleError(f"Invalid role: {role}")
        if getattr(creator, "role", None) == "field_officer":
            creator_lga_id = UserService._get_lga_id(getattr(creator, "lga", None))
            data_lga_id = UserService._get_lga_id(data.get("lga"))
            if data_lga_id != creator_lga_id:
                raise LGAAccessDenied("Cannot create user outside your LGA")
        return UserRepository.create(data)

    @staticmethod
    def get_by_id(user_id: Any) -> Any:
        """Retrieve a user by ID."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    @staticmethod
    def update(user_id: Any, data: dict, updater: Any) -> Any:
        """Update a user with LGA access control."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if getattr(updater, "role", None) == "field_officer":
            user_lga_id = UserService._get_lga_id(getattr(user, "lga", None))
            updater_lga_id = UserService._get_lga_id(getattr(updater, "lga", None))
            if user_lga_id != updater_lga_id:
                raise LGAAccessDenied("Cannot update user outside your LGA")
        return UserRepository.update(user_id, data)

    @staticmethod
    def delete(user_id: Any, deleter: Any) -> None:
        """Delete a user with LGA access control."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if getattr(deleter, "role", None) == "field_officer":
            user_lga_id = UserService._get_lga_id(getattr(user, "lga", None))
            deleter_lga_id = UserService._get_lga_id(getattr(deleter, "lga", None))
            if user_lga_id != deleter_lga_id:
                raise LGAAccessDenied("Cannot delete user outside your LGA")
        return UserRepository.delete(user_id)


class LGAService:
    """Business logic for LGA operations."""

    @staticmethod
    def get_all() -> Any:
        """Return all LGAs."""
        return LGARepository.get_all()

    @staticmethod
    def get_by_id(lga_id: Any) -> Any:
        """Retrieve an LGA by ID."""
        lga = LGARepository.get_by_id(lga_id)
        if not lga:
            raise LGANotFoundError()
        return lga

    @staticmethod
    def get_by_code(code: str) -> Any:
        """Retrieve an LGA by code."""
        lga = LGARepository.get_by_code(code)
        if not lga:
            raise LGANotFoundError()
        return lga
