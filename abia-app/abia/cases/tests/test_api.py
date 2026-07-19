import pytest


@pytest.mark.django_db
class TestCaseAPI:
    def test_list_cases(self, auth_client, test_case):
        response = auth_client.get('/api/v1/cases/')
        assert response.status_code == 200

    def test_create_case(self, auth_client, test_migrant, admin_user):
        data = {
            'title': 'New Case',
            'case_type': 'legal',
            'priority': 'high',
            'status': 'open',
            'migrant': str(test_migrant.id),
            'assigned_to': admin_user.id,
            'description': 'Test'
        }
        response = auth_client.post('/api/v1/cases/', data)
        assert response.status_code == 201

    def test_case_actions(self, auth_client, test_case):
        response = auth_client.post(f'/api/v1/cases/{test_case.id}/assign/')
        assert response.status_code == 200

    def test_case_stats(self, auth_client):
        response = auth_client.get('/api/v1/cases/stats/')
        assert response.status_code == 200
