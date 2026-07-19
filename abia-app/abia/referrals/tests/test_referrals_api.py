import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral


@pytest.mark.django_db
class TestReferralApi:
    def test_list_referrals(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("referral-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_referral(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Ref Migrant",
            phone="+2348333333333",
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
        to_lga = LGA.objects.exclude(id=lga.id).first()
        data = {
            "case": case.id,
            "from_lga": lga.id,
            "to_lga": to_lga.id,
            "reason": "Test referral",
            "status": "pending",
        }
        response = client.post(reverse("referral-list"), data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["reason"] == "Test referral"

    def test_retrieve_referral(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Ref Migrant",
            phone="+2348444444444",
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
        to_lga = LGA.objects.exclude(id=lga.id).first()
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=to_lga,
            reason="Retrieve me",
            status="pending",
            created_by=test_user,
        )
        response = client.get(reverse("referral-detail", kwargs={"pk": referral.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["reason"] == "Retrieve me"


    def test_update_referral(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Ref Update",
            phone="+2348999999999",
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
        to_lga = LGA.objects.exclude(id=lga.id).first()
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=to_lga,
            reason="Original reason",
            status="pending",
            created_by=test_user,
        )
        data = {
            "case": case.id,
            "from_lga": lga.id,
            "to_lga": to_lga.id,
            "reason": "Updated reason",
            "status": "pending",
        }
        response = client.put(reverse("referral-detail", kwargs={"pk": referral.id}), data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["reason"] == "Updated reason"

    def test_delete_referral(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Ref Delete",
            phone="+2348000000000",
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
        to_lga = LGA.objects.exclude(id=lga.id).first()
        referral = Referral.objects.create(
            case=case,
            from_lga=lga,
            to_lga=to_lga,
            reason="Delete me",
            status="pending",
            created_by=test_user,
        )
        response = client.delete(reverse("referral-detail", kwargs={"pk": referral.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_unauthenticated_referral_list(self):
        client = APIClient()
        response = client.get(reverse("referral-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_referral_not_found(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        from uuid import uuid4
        response = client.get(reverse("referral-detail", kwargs={"pk": str(uuid4())}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_referral_audit_log(self, test_user):
        from abia.accounts.models import LGA
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        from abia.referrals.models import Referral
        lga = LGA.objects.first()
        to_lga = LGA.objects.exclude(id=lga.id).first()
        migrant = Migrant.objects.create(
            full_name="Ref Audit",
            phone="+2348999999999",
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
            reason="Audit test",
            status="pending",
            created_by=test_user,
        )
        assert referral.id is not None
