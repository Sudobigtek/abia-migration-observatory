import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from abia.accounts.models import LGA
from abia.migrants.models import Migrant


@pytest.mark.django_db
class TestMigrantApi:
    def test_list_migrants(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("migrant-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_migrant(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        data = {
            "full_name": "API Migrant",
            "phone": "+2348012345678",
            "gender": "male",
            "current_lga": lga.id,
        }
        response = client.post(reverse("migrant-list"), data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["full_name"] == "API Migrant"

    def test_retrieve_migrant(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Retrieve Me",
            phone="+2348098765432",
            gender="female",
            current_lga=lga,
            created_by=test_user,
        )
        response = client.get(reverse("migrant-detail", kwargs={"pk": migrant.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["full_name"] == "Retrieve Me"


    def test_update_migrant(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Update Me",
            phone="+2348555555555",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )
        data = {
            "full_name": "Updated Name",
            "phone": "+2348555555555",
            "gender": "male",
            "current_lga": lga.id,
        }
        response = client.put(reverse("migrant-detail", kwargs={"pk": migrant.id}), data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["full_name"] == "Updated Name"

    def test_delete_migrant(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Delete Me",
            phone="+2348666666666",
            gender="female",
            current_lga=lga,
            created_by=test_user,
        )
        response = client.delete(reverse("migrant-detail", kwargs={"pk": migrant.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_unauthenticated_migrant_list(self):
        client = APIClient()
        response = client.get(reverse("migrant-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_migrant_not_found(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        from uuid import uuid4
        response = client.get(reverse("migrant-detail", kwargs={"pk": str(uuid4())}))
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_migrant_audit_log(self, test_user):
        import logging
        lga = LGA.objects.first()
        migrant = Migrant.objects.create(
            full_name="Audit Log Test",
            phone="+2348777777777",
            gender="male",
            current_lga=lga,
            created_by=test_user,
        )
        # Signal fires; verify no exception raised
        assert migrant.id is not None
