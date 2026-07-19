import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from abia.accounts.models import LGA, User


@pytest.mark.django_db
class TestLGAApi:
    def test_list_lgas(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("lga-list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 17
        assert len(response.data["results"]) == 17

    def test_retrieve_lga(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        response = client.get(reverse("lga-detail", kwargs={"pk": lga.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == lga.name


@pytest.mark.django_db
class TestUserApi:
    def test_list_users(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("user-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_user(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        data = {
            "username": "apinewuser",
            "password": "TestPass123",
            "role": "field_officer",
            "lga": lga.id,
        }
        response = client.post(reverse("user-list"), data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "apinewuser"

    def test_retrieve_user(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        response = client.get(reverse("user-detail", kwargs={"pk": test_user.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == test_user.username


    def test_update_user(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        data = {
            "username": test_user.username,
            "email": "updated@example.com",
            "role": test_user.role,
            "lga": lga.id,
        }
        response = client.put(reverse("user-detail", kwargs={"pk": test_user.id}), data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "updated@example.com"

    def test_delete_user(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        lga = LGA.objects.first()
        victim = User.objects.create_user(
            username="victimuser",
            password="VictimPass123",
            role="field_officer",
            lga=lga,
        )
        response = client.delete(reverse("user-detail", kwargs={"pk": victim.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_unauthenticated_lga_list(self):
        client = APIClient()
        response = client.get(reverse("lga-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_found(self, test_user):
        client = APIClient()
        client.force_authenticate(user=test_user)
        from uuid import uuid4
        response = client.get(reverse("user-detail", kwargs={"pk": str(uuid4())}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_obtain_token(self, test_user):
        test_user.set_password("testpass123")
        test_user.save()
        client = APIClient()
        response = client.post(reverse("token-auth"), {
            "username": test_user.username,
            "password": "testpass123",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_token_authenticated_request(self, test_user):
        from rest_framework.authtoken.models import Token
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=test_user)
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = client.get(reverse("lga-list"))
        assert response.status_code == status.HTTP_200_OK


    def test_token_auto_created_on_user_create(self, test_user):
        from rest_framework.authtoken.models import Token
        assert Token.objects.filter(user=test_user).exists()
