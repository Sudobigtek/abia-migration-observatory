from typing import Any

from common.exceptions import (
    CaseNotFoundError,
    InvalidPriorityError,
    InvalidStatusTransitionError,
    LGAAccessDenied,
)

from .repositories import CaseRepository

VALID_CASE_TRANSITIONS = {
    "open": {"in_progress", "closed", "cancelled"},
    "in_progress": {"resolved", "escalated", "closed"},
    "resolved": {"closed", "reopened"},
    "escalated": {"in_progress", "closed"},
    "closed": {"reopened"},
    "cancelled": {"reopened"},
    "reopened": {"in_progress", "closed"},
}

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


class CaseService:
    """Business logic for case management."""

    @staticmethod
    def _get_lga_id(lga_obj: Any) -> Any:
        """Extract an LGA ID from an object or return the raw ID."""
        return lga_obj.id if hasattr(lga_obj, "id") else lga_obj

    @staticmethod
    def get_by_id(case_id: Any) -> Any:
        """Retrieve a case by ID."""
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError()
        return case

    @staticmethod
    def get_cases_for_request(request: Any) -> Any:
        """Return cases visible to the requesting user."""
        user = request.user
        role = getattr(user, "role", None)
        if role in ("state_admin", "super_admin"):
            return CaseRepository.get_all()
        lga = getattr(user, "lga", None)
        lga_id = lga.id if lga and hasattr(lga, "id") else getattr(user, "lga_id", None)
        return CaseRepository.get_by_lga(lga_id)

    @staticmethod
    def create_case(data: dict, officer: Any) -> Any:
        """Create a case with LGA access control."""
        priority = data.get("priority")
        if priority is not None and priority not in VALID_PRIORITIES:
            raise InvalidPriorityError(f"Invalid priority: {priority}")
        if getattr(officer, "role", None) == "field_officer":
            case_lga_id = CaseService._get_lga_id(data.get("lga"))
            officer_lga_id = CaseService._get_lga_id(getattr(officer, "lga", None))
            if case_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot create case outside your LGA")
        data["created_by"] = officer
        return CaseRepository.create(data)

    @staticmethod
    def update_case(case_id: Any, data: dict, officer: Any) -> Any:
        """Update a case with LGA access control."""
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError()
        if getattr(officer, "role", None) == "field_officer":
            case_lga_id = CaseService._get_lga_id(getattr(case, "lga", None))
            officer_lga_id = CaseService._get_lga_id(getattr(officer, "lga", None))
            if case_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot update case outside your LGA")
        return CaseRepository.update(case_id, data)

    @staticmethod
    def delete_case(case_id: Any, officer: Any) -> Any:
        """Delete a case with LGA access control."""
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError()
        if getattr(officer, "role", None) == "field_officer":
            case_lga_id = CaseService._get_lga_id(getattr(case, "lga", None))
            officer_lga_id = CaseService._get_lga_id(getattr(officer, "lga", None))
            if case_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot delete case outside your LGA")
        return CaseRepository.delete(case_id)

    @staticmethod
    def update_status(case_id: Any, new_status: str, officer: Any) -> Any:
        """Transition a case to a new status if valid."""
        case = CaseRepository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError()
        if getattr(officer, "role", None) == "field_officer":
            case_lga_id = CaseService._get_lga_id(getattr(case, "lga", None))
            officer_lga_id = CaseService._get_lga_id(getattr(officer, "lga", None))
            if case_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot update case outside your LGA")
        current = case.status
        allowed = VALID_CASE_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise InvalidStatusTransitionError()
        return CaseRepository.update(case_id, {"status": new_status})
