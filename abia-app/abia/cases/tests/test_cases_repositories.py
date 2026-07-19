import pytest
from uuid import uuid4
from abia.cases.models import Case
from abia.cases.repositories import CaseRepository
from abia.accounts.models import LGA
from abia.migrants.models import Migrant


@pytest.mark.django_db
class TestCaseRepository:
    def test_get_all(self, test_user):
        assert CaseRepository.get_all().count() == 0

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
        result = CaseRepository.get_by_id(case.id)
        assert result == case

    def test_get_by_id_not_found(self):
        result = CaseRepository.get_by_id(uuid4())
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
        results = CaseRepository.get_by_lga(lga.id)
        assert case in list(results)

    def test_get_by_migrant(self, test_user):
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
        results = CaseRepository.get_by_migrant(migrant.id)
        assert case in list(results)

    def test_create(self, test_user):
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="John Doe",
            phone="+2348012345678",
            current_lga=lga,
            created_by=test_user,
        )
        case = CaseRepository.create({
            "migrant": migrant,
            "lga": lga,
            "status": "open",
            "priority": "medium",
            "created_by": test_user,
        })
        assert case.status == "open"
        assert case.priority == "medium"

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
        updated = CaseRepository.update(case.id, {"status": "in_progress"})
        assert updated.status == "in_progress"
