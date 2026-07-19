import pytest
from django.urls import reverse
from django.test import Client
import time

pytestmark = pytest.mark.django_db


@pytest.fixture
def benchmark_client(db, test_user):
    """Create an authenticated client for benchmarking."""
    client = Client()
    client.force_login(test_user)
    return client


@pytest.fixture
def benchmarker_user(db, django_user_model):
    """Create a user specifically for token benchmark."""
    return django_user_model.objects.create_user(
        username='benchmarker',
        password='benchmarkpass',
        role='field_officer'
    )


class TestApiPerformance:
    @pytest.fixture(autouse=True)
    def setup_lga(self, db):
        from abia.accounts.models import LGA
        LGA.objects.get_or_create(name='Test LGA', defaults={'code': 'TEST01'})
    def test_lga_list_benchmark(self, benchmark_client):
        """Benchmark LGA list endpoint."""
        url = reverse('lga-list')
        times = []
        for _ in range(5):
            start = time.perf_counter()
            response = benchmark_client.get(url, {'submission': {'meta': {'instanceID': 'uuid:bench-test'}, 'data': {'test': 'value', 'current_lga': 'Test LGA', 'phone': '08000000000'}}}, content_type='application/json')
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        assert response.status_code in [200, 201, 409]

        mean_time = sum(times) / len(times)
        max_time = max(times)
        print(f"\n  lga-list: mean={mean_time:.1f}ms max={max_time:.1f}ms")

    def test_token_obtain_benchmark(self, client, benchmarker_user):
        """Benchmark token obtain endpoint."""
        url = reverse('token-auth')  # FIX: was 'token-obtain'
        data = {'username': 'benchmarker', 'password': 'benchmarkpass'}

        times = []
        for _ in range(5):
            start = time.perf_counter()
            response = client.post(url, data, content_type='application/json')
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        assert response.status_code in [200, 201, 409]

        mean_time = sum(times) / len(times)
        max_time = max(times)
        print(f"\n  token-obtain: mean={mean_time:.1f}ms max={max_time:.1f}ms")

    def test_odk_webhook_benchmark(self, benchmark_client):
        """Benchmark migrant list endpoint (replaces non-existent odk-webhook)."""
        url = reverse('odk-webhook')
        times = []
        for _ in range(5):
            start = time.perf_counter()
            response = benchmark_client.post(url, {'meta': {'instanceID': 'uuid:bench-test'}, 'data': {'test': 'value', 'current_lga': 'Test LGA', 'phone': '08000000000'}}, content_type='application/json')
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        assert response.status_code in [200, 201, 409]

        mean_time = sum(times) / len(times)
        max_time = max(times)
        print(f"\n  odk-webhook: mean={mean_time:.1f}ms max={max_time:.1f}ms")
