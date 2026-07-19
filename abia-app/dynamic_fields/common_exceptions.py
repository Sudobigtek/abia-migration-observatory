"""Custom domain exceptions for the Abia Migration Observatory Platform.

All exceptions inherit from AbiaBaseException to enable unified error handling
across the platform. Never raise bare Exception or ValueError (Architecture Contract §1.3).
"""


class AbiaBaseException(Exception):
    """Base exception for all Abia platform errors.

    Attributes:
        message: Human-readable error description.
        code: Machine-readable error code for API responses.
        status_code: HTTP status code for API responses.
    """

    def __init__(self, message: str, code: str = "abia_error", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def __str__(self):
        return f"[{self.code}] {self.message}"


# ───────────────────────────────────────────────────────────────
# LGA-related exceptions
# ───────────────────────────────────────────────────────────────


class LGANotFoundError(AbiaBaseException):
    """Raised when an LGA lookup fails (invalid ID or name)."""

    def __init__(self, lga_identifier: str):
        super().__init__(
            message=f"LGA not found: {lga_identifier}",
            code="lga_not_found",
            status_code=404,
        )


class LGAAccessDenied(AbiaBaseException):
    """Raised when a user attempts to access data outside their LGA.

    Enforces Row-Level Security (RLS) at the service layer.
    """

    def __init__(self, message: str = "Access denied: data outside your LGA"):
        super().__init__(
            message=message,
            code="lga_access_denied",
            status_code=403,
        )


# ───────────────────────────────────────────────────────────────
# User-related exceptions
# ───────────────────────────────────────────────────────────────


class UserNotFoundError(AbiaBaseException):
    """Raised when a user lookup fails."""

    def __init__(self, user_id: str):
        super().__init__(
            message=f"User not found: {user_id}",
            code="user_not_found",
            status_code=404,
        )


class InvalidRoleError(AbiaBaseException):
    """Raised when an invalid role string is provided."""

    def __init__(self, role: str):
        super().__init__(
            message=f"Invalid role: {role}. Valid roles: field_officer, lga_coordinator, state_admin, super_admin",
            code="invalid_role",
            status_code=422,
        )


class DuplicateUserError(AbiaBaseException):
    """Raised when attempting to create a user with duplicate credentials."""

    def __init__(self, identifier: str):
        super().__init__(
            message=f"User already exists: {identifier}",
            code="duplicate_user",
            status_code=409,
        )


# ───────────────────────────────────────────────────────────────
# Migrant-related exceptions
# ───────────────────────────────────────────────────────────────


class MigrantNotFoundError(AbiaBaseException):
    """Raised when a migrant lookup fails."""

    def __init__(self, migrant_id: str):
        super().__init__(
            message=f"Migrant not found: {migrant_id}",
            code="migrant_not_found",
            status_code=404,
        )


class DuplicateMigrantError(AbiaBaseException):
    """Raised when attempting to create a migrant with duplicate identifying info.

    Typically triggered by duplicate phone number or NIN.
    """

    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"Migrant with {field} '{value}' already exists",
            code="duplicate_migrant",
            status_code=409,
        )


# ───────────────────────────────────────────────────────────────
# Case-related exceptions
# ───────────────────────────────────────────────────────────────


class CaseNotFoundError(AbiaBaseException):
    """Raised when a case lookup fails."""

    def __init__(self, case_id: str):
        super().__init__(
            message=f"Case not found: {case_id}",
            code="case_not_found",
            status_code=404,
        )


class InvalidStatusTransitionError(AbiaBaseException):
    """Raised when an invalid case status transition is attempted.

    Valid transitions: open -> in_progress -> resolved/on_hold
    """

    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            message=f"Invalid status transition: {from_status} -> {to_status}",
            code="invalid_status_transition",
            status_code=422,
        )


class InvalidPriorityError(AbiaBaseException):
    """Raised when an invalid case priority is provided."""

    def __init__(self, priority: str):
        super().__init__(
            message=f"Invalid priority: {priority}. Valid: low, medium, high, urgent",
            code="invalid_priority",
            status_code=422,
        )


class CaseAssignmentError(AbiaBaseException):
    """Raised when a case assignment fails (e.g., user in different LGA)."""

    def __init__(self, message: str = "Case assignment failed"):
        super().__init__(
            message=message,
            code="case_assignment_error",
            status_code=422,
        )


# ───────────────────────────────────────────────────────────────
# Referral-related exceptions
# ───────────────────────────────────────────────────────────────


class ReferralNotFoundError(AbiaBaseException):
    """Raised when a referral lookup fails."""

    def __init__(self, referral_id: str):
        super().__init__(
            message=f"Referral not found: {referral_id}",
            code="referral_not_found",
            status_code=404,
        )


class InvalidReferralStatusError(AbiaBaseException):
    """Raised when an invalid referral status transition is attempted.

    Valid transitions: pending -> accepted -> completed
                         pending -> rejected
    """

    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            message=f"Invalid referral status transition: {from_status} -> {to_status}",
            code="invalid_referral_status",
            status_code=422,
        )


class SelfReferralError(AbiaBaseException):
    """Raised when attempting to create a referral to the same LGA."""

    def __init__(self, lga_id: str):
        super().__init__(
            message=f"Cannot create referral within the same LGA: {lga_id}. Use case management instead.",
            code="self_referral",
            status_code=422,
        )


class ReferralAlreadyProcessedError(AbiaBaseException):
    """Raised when attempting to modify a referral that is already completed or rejected."""

    def __init__(self, status: str):
        super().__init__(
            message=f"Referral already in final status: {status}. No further changes allowed.",
            code="referral_already_processed",
            status_code=409,
        )


# ───────────────────────────────────────────────────────────────
# General validation exceptions
# ───────────────────────────────────────────────────────────────


class ValidationError(AbiaBaseException):
    """Raised when input data fails business validation rules.

    Used for field-level validation, format checks, and business rule violations.
    """

    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=f"Validation error{f' [{field}]' if field else ''}: {message}",
            code="validation_error",
            status_code=400,
        )


class AuthenticationError(AbiaBaseException):
    """Raised when authentication fails or token is invalid."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="authentication_error",
            status_code=401,
        )


class AuthorizationError(AbiaBaseException):
    """Raised when authenticated user lacks permission for an action.

    Distinct from LGAAccessDenied (which is LGA-scoped).
    """

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="authorization_error",
            status_code=403,
        )
