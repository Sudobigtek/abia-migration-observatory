"""Tests for monitoring middleware and health endpoints."""

import pytest
from django.urls import reverse

from django.test import Client


class TestHealthEndpoint:
    """Test /health/ endpoint per Architecture Contract §13."""

    @pytest.mark.django_db
    def test_health_check_ok(self):
        """Given DB reachable, return 200 healthy."""
        client = Client()
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert data["checks"].get("django") is True
        assert data["checks"].get("database") is True

    @pytest.mark.django_db
    def test_health_check_method_post(self):
        """Given POST to /health/, still return 200 (idempotent)."""
        client = Client()
        response = client.post("/health/")
        assert response.status_code == 200


class TestMetricsEndpoint:
    """Test /metrics/ endpoint for Prometheus."""

    def test_metrics_returns_prometheus_format(self):
        """Given GET /metrics/, return Prometheus text format."""
        client = Client()
        response = client.get("/metrics/")
        assert response.status_code == 200
        assert "django_http_requests_total" in response.content.decode()

    def test_metrics_content_type(self):
        """Given GET /metrics/, return correct content type."""
        client = Client()
        response = client.get("/metrics/")
        assert response["Content-Type"] == "text/plain; version=0.0.4; charset=utf-8"
