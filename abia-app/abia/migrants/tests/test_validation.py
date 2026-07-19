import pytest
from django.core.exceptions import ValidationError
from abia.migrants.models import Migrant


@pytest.mark.django_db
def test_migrant_phone_validation(test_user):
    from abia.accounts.models import LGA
    lga = LGA.objects.first()
    m = Migrant(
        full_name="Bad Phone",
        phone="12345",
        gender="male",
        current_lga=lga,
        created_by=test_user,
    )
    with pytest.raises(ValidationError) as exc:
        m.full_clean()
    assert "phone" in exc.value.message_dict


@pytest.mark.django_db
def test_migrant_missing_lga(test_user):
    m = Migrant(
        full_name="No LGA",
        phone="+2348111111111",
        gender="male",
        created_by=test_user,
    )
    with pytest.raises(ValidationError) as exc:
        m.full_clean()
    assert "current_lga" in exc.value.message_dict
