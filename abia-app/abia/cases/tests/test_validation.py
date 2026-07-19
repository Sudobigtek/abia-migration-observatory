import pytest
from django.core.exceptions import ValidationError
from abia.cases.models import Case


@pytest.mark.django_db
def test_case_missing_migrant(test_user):
    from abia.accounts.models import LGA
    lga = LGA.objects.first()
    c = Case(lga=lga, status="open", priority="medium", created_by=test_user)
    with pytest.raises(ValidationError) as exc:
        c.full_clean()
    assert "migrant" in exc.value.message_dict


@pytest.mark.django_db
def test_case_missing_lga(test_user):
    from abia.migrants.models import Migrant
    from abia.accounts.models import LGA
    lga = LGA.objects.first()
    migrant = Migrant.objects.create(
        full_name="Case LGA Test",
        phone="+2348111111111",
        gender="male",
        current_lga=lga,
        created_by=test_user,
    )
    c = Case(migrant=migrant, status="open", priority="medium", created_by=test_user)
    with pytest.raises(ValidationError) as exc:
        c.full_clean()
    assert "lga" in exc.value.message_dict
