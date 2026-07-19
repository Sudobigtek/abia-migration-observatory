import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.cases.models import Case


@pytest.mark.django_db
class TestCaseApi:
    def test_list_cases(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("case-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_case(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Case Migrant",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )
        data = {
            "migrant": migrant.id,
            "case_type": "irregular_migration",
            "description": "Test case",
            "status": "open",
            "priority": "medium",
            "lga": lga.id,
        }
        response = client.post(reverse("case-list"), data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["case_type"] == "irregular_migration"

    def test_retrieve_case(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Case Migrant",
            phone="+2348222222222",
            gender="female",
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
        response = client.get(reverse("case-detail", kwargs={"pk": case.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "open"


    def test_update_case(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Case Update",
            phone="+2348777777777",
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
        data = {
            "migrant": migrant.id,
            "case_type": "trafficking",
            "description": "Updated description",
            "status": "open",
            "priority": "high",
            "lga": lga.id,
        }
        response = client.put(reverse("case-detail", kwargs={"pk": case.id}), data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["priority"] == "high"

    def test_delete_case(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Case Delete",
            phone="+2348888888888",
            gender="female",
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
        response = client.delete(reverse("case-detail", kwargs={"pk": case.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_unauthenticated_case_list(self):
        client = APIClient()
        response = client.get(reverse("case-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_case_not_found(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        from uuid import uuid4
        response = client.get(reverse("case-detail", kwargs={"pk": str(uuid4())}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nested_referrals(self, test_user):
        from abia.accounts.models import LGA
        from abia.migrants.models import Migrant
        from abia.referrals.models import Referral
        from abia.cases.models import Case
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        to_lga = LGA.objects.exclude(id=lga.id).first()
        migrant = Migrant.objects.create(
            full_name="Nested Ref",
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
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=to_lga,
            reason="Nested test",
            status="pending",
            created_by=test_user,
        )
        response = client.get(reverse("case-referrals", kwargs={"pk": case.id}))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["reason"] == "Nested test"


    def test_case_audit_log(self, test_user):
        from abia.accounts.models import LGA
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Case Audit",
            phone="+2348888888888",
            gender="female",
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
        assert case.id is not None
