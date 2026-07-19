class DynamicFieldError(Exception):
    pass


class FieldTypeError(DynamicFieldError):
    pass


class ValidationError(DynamicFieldError):
    pass


class EntityNotFoundError(DynamicFieldError):
    pass


class DuplicateFieldError(DynamicFieldError):
    pass


class PermissionDeniedError(DynamicFieldError):
    pass
