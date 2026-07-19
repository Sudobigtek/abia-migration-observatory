import pytest
from django.core.exceptions import ValidationError
from abia.referrals.models import Referral


@pytest.mark.django_db
def test_referral_same_lga(test_user):
    from abia.accounts.models import LGA
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    lga = LGA.objects.first()
    migrant = Migrant.objects.create(
        full_name="Ref Same LGA",
        phone="+2348111111111",
        gender="male",
        current_lga=lga,
        created_by=test_user,
    )
    case = Case.objects.create(
        migrant=migrant,
        lga=lga,
        status="open",
        priority="medium",
        created_by=test_user,
    )
    r = Referral(
        case=case,
        from_lga=lga,
        to_lga=lga,
        reason="Same LGA",
        status="pending",
        created_by=test_user,
    )
    with pytest.raises(ValidationError) as exc:
        r.full_clean()
    assert "to_lga" in exc.value.message_dict


@pytest.mark.django_db
def test_referral_missing_case(test_user):
    from abia.accounts.models import LGA
    lga = LGA.objects.first()
    r = Referral(
        from_lga=lga,
        to_lga=LGA.objects.exclude(id=lga.id).first(),
        reason="No case",
        status="pending",
        created_by=test_user,
    )
    with pytest.raises(ValidationError) as exc:
        r.full_clean()
    assert "case" in exc.value.message_dict
