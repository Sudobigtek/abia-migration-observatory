"""Custom domain exceptions for the Abia Migration Observatory Platform.

All exceptions inherit from AbiaBaseException.
Never raise bare Exception or ValueError (Architecture Contract §1.3).
"""


class AbiaBaseException(Exception):
    """Base exception for all Abia platform errors."""

    def __init__(self, message, code="abia_error", status_code=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def __str__(self):
        return f"[{self.code}] {self.message}"


class LGANotFoundError(AbiaBaseException):
    def __init__(self, identifier):
        super().__init__(f"LGA not found: {identifier}", "lga_not_found", 404)


class LGAAccessDenied(AbiaBaseException):
    def __init__(self, message="Access denied: data outside your LGA"):
        super().__init__(message, "lga_access_denied", 403)


class UserNotFoundError(AbiaBaseException):
    def __init__(self, user_id):
        super().__init__(f"User not found: {user_id}", "user_not_found", 404)


class InvalidRoleError(AbiaBaseException):
    def __init__(self, role):
        super().__init__(f"Invalid role: {role}", "invalid_role", 422)


class MigrantNotFoundError(AbiaBaseException):
    def __init__(self, migrant_id):
        super().__init__(f"Migrant not found: {migrant_id}", "migrant_not_found", 404)


class CaseNotFoundError(AbiaBaseException):
    def __init__(self, case_id):
        super().__init__(f"Case not found: {case_id}", "case_not_found", 404)


class InvalidStatusTransitionError(AbiaBaseException):
    def __init__(self, from_status, to_status):
        super().__init__(
            f"Invalid status transition: {from_status} -> {to_status}",
            "invalid_status_transition",
            422,
        )


class InvalidPriorityError(AbiaBaseException):
    def __init__(self, priority):
        super().__init__(f"Invalid priority: {priority}", "invalid_priority", 422)


class ReferralNotFoundError(AbiaBaseException):
    def __init__(self, referral_id):
        super().__init__(
            f"Referral not found: {referral_id}", "referral_not_found", 404
        )


class InvalidReferralStatusError(AbiaBaseException):
    def __init__(self, from_status, to_status):
        super().__init__(
            f"Invalid referral status transition: {from_status} -> {to_status}",
            "invalid_referral_status",
            422,
        )


class SelfReferralError(AbiaBaseException):
    def __init__(self, lga_id):
        super().__init__(
            f"Cannot create referral within the same LGA: {lga_id}",
            "self_referral",
            422,
        )


class ValidationError(AbiaBaseException):
    def __init__(self, message, field=None):
        super().__init__(
            f"Validation error{f' [{field}]' if field else ''}: {message}",
            "validation_error",
            400,
        )
