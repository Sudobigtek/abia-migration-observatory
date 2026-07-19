import pytest


@pytest.mark.django_db
class TestReferralAPI:
    def test_list_referrals(self, auth_client, test_referral):
        response = auth_client.get('/api/v1/referrals/')
        assert response.status_code == 200

    def test_accept_referral(self, auth_client, test_referral):
        response = auth_client.post(f'/api/v1/referrals/{test_referral.id}/accept/')
        assert response.status_code == 200
        assert response.data['status'] == 'accepted'

    def test_referral_stats(self, auth_client):
        response = auth_client.get('/api/v1/referrals/stats/')
        assert response.status_code == 200
