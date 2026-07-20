"""Custom domain exceptions for Abia Migration Observatory."""


class AbiaBaseException(Exception):
    """Base exception for all domain errors."""
    pass


class LGAAccessDenied(AbiaBaseException):
    """Raised when user attempts action outside their LGA jurisdiction."""
    pass


class LGANotFoundError(AbiaBaseException):
    """Raised when referenced LGA does not exist."""
    pass


class DuplicateSubmissionError(AbiaBaseException):
    """Raised when ODK submission ID already processed."""
    pass


class ResourceNotFoundError(AbiaBaseException):
    """Raised when requested resource does not exist."""
    pass


class BusinessRuleViolation(AbiaBaseException):
    """Raised when a business rule is violated."""
    pass


class SyncError(AbiaBaseException):
    """Raised when external sync operation fails."""
    pass