"""Cases business logic layer."""
from .repositories import CaseRepository
from .exceptions import LGAAccessDenied, CaseNotFoundError, InvalidTransitionError

class CaseService:

    @staticmethod
    def get_by_id(case_id):
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError("Case not found")
        return case
    VALID_TRANSITIONS = {
        "open": ["in_progress", "closed", "escalated"],
        "in_progress": ["closed", "escalated", "on_hold"],
        "on_hold": ["in_progress", "closed"],
        "escalated": ["in_progress", "closed"],
        "closed": [],
    }

    @staticmethod
    def get_cases_for_request(request):
        user = request.user
        if user.role in ("state_admin", "super_admin"):
            return CaseRepository.get_all()
        return CaseRepository.get_by_lga(user.lga_id)

    @staticmethod
    def create_case(data, creator):
        if creator.role == "field_officer" and data.get("lga") != creator.lga:
            raise LGAAccessDenied("Cannot create case outside your LGA")
        data["created_by"] = creator
        data["status"] = "open"
        return CaseRepository.create(data)

    @staticmethod
    def get_case_by_id(case_id, requester):
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError()
        if requester.role not in ("state_admin", "super_admin"):
            if case.lga != requester.lga:
                raise LGAAccessDenied()
        return case

    @staticmethod
    def transition_case(case_id, new_status, requester):
        case = CaseService.get_case_by_id(case_id, requester)
        current = case.status
        allowed = CaseService.VALID_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            raise InvalidTransitionError(f"Cannot transition from {current} to {new_status}")
        return CaseRepository.update(case_id, {"status": new_status})
