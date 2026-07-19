"""Tests for Kong API gateway client."""

import pytest
from unittest.mock import patch

from abia.common.kong_client import KongClient


class TestKongClient:
    """Test Kong Admin API client."""

    @patch("abia.common.kong_client.KongClient._request")
    def test_create_service(self, mock_request):
        """Given name and URL, create service."""
        mock_request.return_value = {"id": "svc-123", "name": "abia-api"}

        sid = KongClient.create_service("abia-api", "http://django:8000")

        assert sid == "svc-123"
        mock_request.assert_called_once()
        args = mock_request.call_args[0]
        assert args[0] == "/services"

    @patch("abia.common.kong_client.KongClient._request")
    def test_create_route(self, mock_request):
        """Given service and path, create route."""
        mock_request.return_value = {"id": "route-456"}

        rid = KongClient.create_route("abia-api", "/api/v1/")

        assert rid == "route-456"

    @patch("abia.common.kong_client.KongClient._request")
    def test_add_rate_limiting(self, mock_request):
        """Given service, enable rate limiting."""
        mock_request.return_value = {"id": "plugin-789"}

        pid = KongClient.add_rate_limiting("abia-api", minute=200)

        assert pid == "plugin-789"
        args, kwargs = mock_request.call_args
        assert args[1]["config"]["minute"] == 200

    @patch("abia.common.kong_client.KongClient._request")
    def test_add_key_auth(self, mock_request):
        """Given service, enable key auth."""
        mock_request.return_value = {"id": "plugin-abc"}

        pid = KongClient.add_key_auth("abia-api")

        assert pid == "plugin-abc"

    @patch("abia.common.kong_client.KongClient._request")
    def test_create_consumer(self, mock_request):
        """Given username, create consumer."""
        mock_request.return_value = {"id": "consumer-def"}

        cid = KongClient.create_consumer("field-officer-1")

        assert cid == "consumer-def"

    @patch("abia.common.kong_client.KongClient._request")
    def test_list_services(self, mock_request):
        """Given services, return list."""
        mock_request.return_value = {"data": [{"name": "svc1"}, {"name": "svc2"}]}

        services = KongClient.list_services()

        assert len(services) == 2
