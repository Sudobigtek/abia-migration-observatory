import re
from django.core.exceptions import ValidationError


def validate_nigeria_phone(value):
    if not value:
        return
    if not re.match(r'^\+234\d{10}$', value):
        raise ValidationError(
            "Phone number must be in format +234XXXXXXXXXX (13 characters total)."
        )


def validate_role(value):
    valid = {"field_officer", "state_admin", "super_admin", "lga_coordinator"}
    if value not in valid:
        raise ValidationError(
            f"Role must be one of: {', '.join(sorted(valid))}."
        )
