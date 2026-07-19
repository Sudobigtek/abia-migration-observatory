"""Kong Admin API client.

Per Architecture Contract §2.6:
Kong 3.x for rate limiting, auth, logging.

No external dependency — uses urllib (built-in).
Kong container must be running at KONG_ADMIN_URL.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

logger = logging.getLogger("abia.kong")

KONG_ADMIN_URL = "http://kong:8001"


class KongClient:
    """HTTP client for Kong Admin API."""

    @staticmethod
    def _request(
        path: str,
        data: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make HTTP request to Kong Admin API."""
        url = f"{KONG_ADMIN_URL}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            logger.error("Kong HTTP %s: %s", exc.code, exc.read().decode())
            raise
        except urllib.error.URLError as exc:
            logger.error("Kong unreachable: %s", exc.reason)
            raise

    @staticmethod
    def create_service(name: str, url: str) -> str:
        """Register a backend service."""
        result = KongClient._request(
            "/services",
            {"name": name, "url": url},
            "POST",
        )
        sid = result.get("id", "")
        logger.info("Created Kong service %s: %s", name, sid)
        return sid

    @staticmethod
    def create_route(service_name: str, path: str) -> str:
        """Create a route for a service."""
        result = KongClient._request(
            f"/services/{service_name}/routes",
            {"paths": [path]},
            "POST",
        )
        rid = result.get("id", "")
        logger.info("Created Kong route %s → %s", path, service_name)
        return rid

    @staticmethod
    def add_rate_limiting(service_name: str, minute: int = 100) -> str:
        """Enable rate limiting on a service."""
        result = KongClient._request(
            f"/services/{service_name}/plugins",
            {
                "name": "rate-limiting",
                "config": {
                    "minute": minute,
                    "policy": "local",
                },
            },
            "POST",
        )
        pid = result.get("id", "")
        logger.info("Added rate limiting to %s: %s/min", service_name, minute)
        return pid

    @staticmethod
    def add_key_auth(service_name: str) -> str:
        """Enable API key authentication on a service."""
        result = KongClient._request(
            f"/services/{service_name}/plugins",
            {"name": "key-auth"},
            "POST",
        )
        pid = result.get("id", "")
        logger.info("Added key-auth to %s", service_name)
        return pid

    @staticmethod
    def create_consumer(username: str) -> str:
        """Create a Kong consumer."""
        result = KongClient._request(
            "/consumers",
            {"username": username},
            "POST",
        )
        cid = result.get("id", "")
        logger.info("Created Kong consumer %s: %s", username, cid)
        return cid

    @staticmethod
    def list_services() -> List[Dict[str, Any]]:
        """List all registered services."""
        try:
            result = KongClient._request("/services")
            return result.get("data", [])
        except Exception as exc:
            logger.warning("Failed to list services: %s", exc)
            return []
