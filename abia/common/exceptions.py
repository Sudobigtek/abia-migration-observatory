"""Custom domain exceptions for Abia Migration Observatory."""
class AbiaBaseException(Exception):
    status_code = 500
    default_message = "An unexpected error occurred."
    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class LGAAccessDenied(AbiaBaseException):
    status_code = 403
    default_message = "Access denied: LGA jurisdiction violation."

class RolePermissionDenied(AbiaBaseException):
    status_code = 403
    default_message = "Access denied: insufficient role privileges."

class LGANotFoundError(AbiaBaseException):
    status_code = 404
    default_message = "LGA not found."

class MigrantNotFoundError(AbiaBaseException):
    status_code = 404
    default_message = "Migrant record not found."

class CaseNotFoundError(AbiaBaseException):
    status_code = 404
    default_message = "Case not found."

class ReferralNotFoundError(AbiaBaseException):
    status_code = 404
    default_message = "Referral not found."

class UserNotFoundError(AbiaBaseException):
    status_code = 404
    default_message = "User not found."

class DuplicateSubmissionError(AbiaBaseException):
    status_code = 409
    default_message = "Duplicate submission detected."

class InvalidTransitionError(AbiaBaseException):
    status_code = 422
    default_message = "Invalid state transition."

class ValidationError(AbiaBaseException):
    status_code = 422
    default_message = "Business validation failed."

class EncryptionError(AbiaBaseException):
    status_code = 500
    default_message = "Data encryption operation failed."
