
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.referrals.repositories import ReferralRepository


@pytest.fixture
def from_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def to_lga():
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_user(from_lga):
    return User.objects.create_user(
        username="refuser",
        password="RefPass123!",
        role="field_officer",
        lga=from_lga,
    )


@pytest.fixture
def test_migrant(from_lga):
    return Migrant.objects.create(
        full_name="Referral Subject",
        phone="+2348044444444",
        date_of_birth=date(1988, 8, 8),
        gender="female",
        current_lga=from_lga,
        lga_of_origin=from_lga,
        status="active",
    )


@pytest.fixture
def test_case(test_user, test_migrant, from_lga):
    return Case.objects.create(
        migrant=test_migrant,
        lga=from_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="high",
        case_type="medical",
        description="Case for referral",
    )


@pytest.fixture
def test_referral(test_case, from_lga, to_lga, test_user):
    return Referral.objects.create(
        case=test_case,
        from_lga=from_lga,
        to_lga=to_lga,
        to_organization="Hospital",
        to_contact_name="Dr. Smith",
        to_contact_phone="+2348055555555",
        reason="Medical referral",
        status="pending",
        created_by=test_user,
    )


@pytest.mark.django_db
class TestReferralRepository:
    def test_get_all_referrals(self, test_referral):
        result = ReferralRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_referral):
        result = ReferralRepository.get_by_id(test_referral.id)
        assert result is not None
        assert result.reason == "Medical referral"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = ReferralRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_referral, from_lga):
        result = ReferralRepository.get_by_lga(from_lga.id)
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_case(self, test_referral, test_case):
        result = ReferralRepository.get_by_case(test_case.id)
        assert result.filter(id=test_referral.id).exists()

    def test_create_referral(self, test_case, from_lga, to_lga, test_user):
        data = {
            "case": test_case,
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Clinic",
            "to_contact_name": "Dr. Jones",
            "to_contact_phone": "+2348066666666",
            "reason": "Follow-up",
            "status": "pending",
            "created_by": test_user,
        }
        result = ReferralRepository.create(data)
        assert result.id is not None
        assert result.to_organization == "Clinic"

    def test_update_referral(self, test_referral):
        updated = ReferralRepository.update(test_referral.id, {"status": "in_progress"})
        assert updated.status == "in_progress"
