"""Referrals business logic layer."""
from .repositories import ReferralRepository
from .exceptions import LGAAccessDenied, ReferralNotFoundError, InvalidTransitionError

class ReferralService:
    VALID_TRANSITIONS = {
        "pending": ["accepted", "rejected", "cancelled"],
        "accepted": ["in_transit", "completed", "cancelled"],
        "in_transit": ["completed", "cancelled"],
        "rejected": [],
        "completed": [],
        "cancelled": [],
    }

    @staticmethod
    def get_referrals_for_request(request):
        user = request.user
        if user.role in ("state_admin", "super_admin"):
            return ReferralRepository.get_all()
        return ReferralRepository.get_by_lga(user.lga_id)

    @staticmethod
    def create_referral(data, creator):
        if creator.role == "field_officer":
            if data.get("from_lga") != creator.lga and data.get("to_lga") != creator.lga:
                raise LGAAccessDenied("Referral must involve your LGA")
        data["status"] = "pending"
        data["created_by"] = creator
        return ReferralRepository.create(data)

    @staticmethod
    def get_referral_by_id(referral_id, requester):
        referral = ReferralRepository.get_by_id(referral_id)
        if not referral:
            raise ReferralNotFoundError()
        if requester.role not in ("state_admin", "super_admin"):
            if referral.from_lga != requester.lga and referral.to_lga != requester.lga:
                raise LGAAccessDenied()
        return referral

    @staticmethod
    def transition_referral(referral_id, new_status, requester):
        referral = ReferralService.get_referral_by_id(referral_id, requester)
        current = referral.status
        allowed = ReferralService.VALID_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            raise InvalidTransitionError(f"Cannot transition from {current} to {new_status}")
        return ReferralRepository.update(referral_id, {"status": new_status})
