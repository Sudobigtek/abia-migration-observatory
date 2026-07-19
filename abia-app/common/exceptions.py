"""Custom domain exceptions for the Abia Migration Observatory."""


class AbiaBaseException(Exception):
    """Base for all platform-specific exceptions."""

    pass


class LGAAccessDenied(AbiaBaseException):
    """Raised when a user attempts to access data outside their LGA scope."""

    pass


class UserNotFoundError(AbiaBaseException):
    """Raised when a requested user does not exist."""

    pass


class LGANotFoundError(AbiaBaseException):
    """Raised when a requested LGA does not exist."""

    pass


class ReferralNotFoundError(AbiaBaseException):
    """Raised when a requested referral does not exist."""

    pass


class SelfReferralError(AbiaBaseException):
    """Raised when a referral origin and destination are the same LGA."""

    pass


class InvalidReferralStatusError(AbiaBaseException):
    """Raised when a referral status transition is invalid."""

    def __init__(self, current: str, new: str) -> None:
        self.current = current
        self.new = new
        super().__init__(f"Invalid transition from '{current}' to '{new}'")


class CaseNotFoundError(AbiaBaseException):
    """Raised when a requested case does not exist."""

    pass


class InvalidCaseStatusError(AbiaBaseException):
    """Raised when a case status transition is invalid."""

    def __init__(self, current: str, new: str) -> None:
        self.current = current
        self.new = new
        super().__init__(f"Invalid transition from '{current}' to '{new}'")


class InvalidStatusTransitionError(AbiaBaseException):
    """Alias for InvalidCaseStatusError (expected by tests)."""

    pass


class InvalidPriorityError(AbiaBaseException):
    """Raised when a case priority is not valid."""

    pass


class InvalidRoleError(AbiaBaseException):
    """Raised when a user role is not valid."""

    pass


class DuplicateSubmissionError(AbiaBaseException):
    """Raised when an ODK submission with the same ID has already been processed."""

    pass


class InvalidGPSDataError(AbiaBaseException):
    """Raised when GPS coordinates from an ODK submission are malformed or out of bounds."""

    pass


class MigrantNotFoundError(AbiaBaseException):
    """Raised when a requested migrant does not exist."""

    pass


class DuplicateMigrantError(AbiaBaseException):
    """Raised when a migrant with the same phone already exists."""

    pass


class InvalidPhoneError(AbiaBaseException):
    """Raised when a phone number format is invalid."""

    pass
