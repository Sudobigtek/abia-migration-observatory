
class AbiaBaseException(Exception):
    def __init__(self, message, code="abia_error", status_code=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class LGANotFoundError(AbiaBaseException):
    def __init__(self, identifier):
        super().__init__(f"LGA not found: {identifier}", "lga_not_found", 404)


class LGAAccessDenied(AbiaBaseException):
    def __init__(self, message="Access denied"):
        super().__init__(message, "lga_access_denied", 403)


class UserNotFoundError(AbiaBaseException):
    def __init__(self, uid):
        super().__init__(f"User not found: {uid}", "user_not_found", 404)


class InvalidRoleError(AbiaBaseException):
    def __init__(self, role):
        super().__init__(f"Invalid role: {role}", "invalid_role", 422)


class MigrantNotFoundError(AbiaBaseException):
    def __init__(self, mid):
        super().__init__(f"Migrant not found: {mid}", "migrant_not_found", 404)


class DuplicateMigrantError(AbiaBaseException):
    def __init__(self, phone):
        super().__init__(f"Migrant with phone {phone} already exists", "duplicate_migrant", 409)


class InvalidPhoneError(AbiaBaseException):
    def __init__(self, phone):
        super().__init__(f"Invalid phone number: {phone}", "invalid_phone", 422)


class CaseNotFoundError(AbiaBaseException):
    def __init__(self, cid):
        super().__init__(f"Case not found: {cid}", "case_not_found", 404)


class InvalidStatusTransitionError(AbiaBaseException):
    def __init__(self, fr, to):
        super().__init__(f"Invalid transition: {fr} -> {to}", "invalid_status_transition", 422)


class InvalidPriorityError(AbiaBaseException):
    def __init__(self, p):
        super().__init__(f"Invalid priority: {p}", "invalid_priority", 422)


class ReferralNotFoundError(AbiaBaseException):
    def __init__(self, rid):
        super().__init__(f"Referral not found: {rid}", "referral_not_found", 404)


class InvalidReferralStatusError(AbiaBaseException):
    def __init__(self, fr, to):
        super().__init__(f"Invalid referral transition: {fr} -> {to}", "invalid_referral_status", 422)


class SelfReferralError(AbiaBaseException):
    def __init__(self, lga_id):
        super().__init__(f"Cannot create referral within same LGA: {lga_id}", "self_referral", 422)


class ValidationError(AbiaBaseException):
    def __init__(self, message, field=None):
        super().__init__(f"Validation error: {message}", "validation_error", 400)
