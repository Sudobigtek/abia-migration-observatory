import pytest


@pytest.mark.django_db
class TestMigrantAPI:
    def test_list_migrants(self, auth_client, test_migrant):
        response = auth_client.get('/api/v1/migrants/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_create_migrant(self, auth_client, test_lga):
        data = {
            'full_name': 'New Migrant',
            'gender': 'female',
            'phone': '+2348099999999',
            'current_lga': test_lga.id,
            'status': 'active'
        }
        response = auth_client.post('/api/v1/migrants/', data)
        assert response.status_code == 201
        assert response.data['full_name'] == 'New Migrant'

    def test_migrant_stats(self, auth_client):
        response = auth_client.get('/api/v1/migrants/stats/')
        assert response.status_code == 200
        assert 'total_migrants' in response.data

    def test_migrant_map_data(self, auth_client):
        response = auth_client.get('/api/v1/migrants/map_data/')
        assert response.status_code == 200
        assert response.data['type'] == 'FeatureCollection'
