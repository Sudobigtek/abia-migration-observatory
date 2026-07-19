from typing import Any

from common.exceptions import (
    InvalidReferralStatusError,
    LGAAccessDenied,
    ReferralNotFoundError,
    SelfReferralError,
)

from .repositories import ReferralRepository

VALID_REFERRAL_TRANSITIONS = {
    "pending": {"accepted", "rejected"},
    "accepted": {"completed", "cancelled"},
    "rejected": {"pending"},
    "completed": set(),
    "cancelled": set(),
}


class ReferralService:
    """Business logic for inter-LGA referral operations."""

    @staticmethod
    def _get_lga_id(lga_obj: Any) -> Any:
        """Extract an LGA ID from an object or return the raw ID."""
        return lga_obj.id if hasattr(lga_obj, "id") else lga_obj

    @staticmethod
    def get_by_id(referral_id: Any) -> Any:
        """Retrieve a referral by ID."""
        referral = ReferralRepository.get_by_id(referral_id)
        if not referral:
            raise ReferralNotFoundError("Referral not found")
        return referral

    @staticmethod
    def get_referrals_for_case(case_id: Any) -> Any:
        """Return referrals linked to a case."""
        return ReferralRepository.get_by_case(case_id)

    @staticmethod
    def get_referrals_for_request(request: Any) -> Any:
        """Return referrals visible to the requesting user."""
        user = request.user
        role = getattr(user, "role", None)
        if role in ("state_admin", "super_admin"):
            return ReferralRepository.get_all()
        lga = getattr(user, "lga", None)
        lga_id = lga.id if lga and hasattr(lga, "id") else getattr(user, "lga_id", None)
        return ReferralRepository.get_by_lga(lga_id)

    @staticmethod
    def create_referral(data: dict, officer: Any) -> Any:
        """Create a referral with origin/destination validation."""
        from_lga = data.get("from_lga")
        to_lga = data.get("to_lga")
        from_lga_id = ReferralService._get_lga_id(from_lga)
        to_lga_id = ReferralService._get_lga_id(to_lga)
        if from_lga_id == to_lga_id:
            raise SelfReferralError("Cannot refer to the same LGA")
        if getattr(officer, "role", None) == "field_officer":
            officer_lga_id = ReferralService._get_lga_id(getattr(officer, "lga", None))
            if from_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot create referral from outside your LGA")
        data["created_by"] = officer
        return ReferralRepository.create(data)

    @staticmethod
    def update_referral(referral_id: Any, data: dict, officer: Any) -> Any:
        """Update a referral with LGA access control."""
        referral = ReferralRepository.get_by_id(referral_id)
        if not referral:
            raise ReferralNotFoundError("Referral not found")
        if getattr(officer, "role", None) == "field_officer":
            referral_lga_id = ReferralService._get_lga_id(
                getattr(referral, "from_lga", None)
            )
            officer_lga_id = ReferralService._get_lga_id(getattr(officer, "lga", None))
            if referral_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot update referral outside your LGA")
        return ReferralRepository.update(referral_id, data)

    @staticmethod
    def delete_referral(referral_id: Any, officer: Any) -> Any:
        """Delete a referral with LGA access control."""
        referral = ReferralRepository.get_by_id(referral_id)
        if not referral:
            raise ReferralNotFoundError("Referral not found")
        if getattr(officer, "role", None) == "field_officer":
            referral_lga_id = ReferralService._get_lga_id(
                getattr(referral, "from_lga", None)
            )
            officer_lga_id = ReferralService._get_lga_id(getattr(officer, "lga", None))
            if referral_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot delete referral outside your LGA")
        return ReferralRepository.delete(referral_id)

    @staticmethod
    def update_status(referral_id: Any, new_status: str, officer: Any) -> Any:
        """Transition a referral to a new status if valid."""
        referral = ReferralRepository.get_by_id(referral_id)
        if not referral:
            raise ReferralNotFoundError("Referral not found")
        if getattr(officer, "role", None) == "field_officer":
            referral_lga_id = ReferralService._get_lga_id(
                getattr(referral, "from_lga", None)
            )
            officer_lga_id = ReferralService._get_lga_id(getattr(officer, "lga", None))
            if referral_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot update referral outside your LGA")
        current = referral.status
        allowed = VALID_REFERRAL_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise InvalidReferralStatusError(current, new_status)
        return ReferralRepository.update(referral_id, {"status": new_status})
