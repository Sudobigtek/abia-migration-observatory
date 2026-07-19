import pytest
from uuid import uuid4
from abia.referrals.models import Referral
from abia.referrals.repositories import ReferralRepository
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.cases.models import Case


@pytest.mark.django_db
class TestReferralRepository:
    def test_get_all(self, test_user):
        assert ReferralRepository.get_all().count() == 0

    def test_get_by_id(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
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
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=lga,
            status="pending",
            created_by=test_user,
        )
        result = ReferralRepository.get_by_id(referral.id)
        assert result == referral

    def test_get_by_id_not_found(self):
        result = ReferralRepository.get_by_id(uuid4())
        assert result is None

    def test_get_by_lga(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
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
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=lga,
            status="pending",
            created_by=test_user,
        )
        results = ReferralRepository.get_by_lga(lga.id)
        assert referral in list(results)

    def test_get_by_case(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
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
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=lga,
            status="pending",
            created_by=test_user,
        )
        results = ReferralRepository.get_by_case(case.id)
        assert referral in list(results)

    def test_create(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
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
        referral = ReferralRepository.create({
            "case": case,
            "from_lga": lga,
            "to_lga": lga,
            "status": "pending",
            "created_by": test_user,
        })
        assert referral.status == "pending"

    def test_update(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
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
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=lga,
            status="pending",
            created_by=test_user,
        )
        updated = ReferralRepository.update(referral.id, {"status": "accepted"})
        assert updated.status == "accepted"
