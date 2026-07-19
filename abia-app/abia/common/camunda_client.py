"""Camunda REST API client.

Per Architecture Contract §2.3:
Camunda 7.20 for business process automation.

No external dependency — uses urllib (built-in).
Camunda container must be running at CAMUNDA_URL.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

logger = logging.getLogger("abia.camunda")

CAMUNDA_BASE_URL = "http://camunda:8080/engine-rest"


class CamundaClient:
    """HTTP client for Camunda REST API."""

    @staticmethod
    def _request(
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Camunda and parse JSON."""
        url = f"{CAMUNDA_BASE_URL}{path}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data).encode() if data else None

        req = urllib.request.Request(
            url, data=body, headers=headers, method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            logger.error("Camunda HTTP %s: %s", exc.code, exc.read().decode())
            raise
        except urllib.error.URLError as exc:
            logger.error("Camunda unreachable: %s", exc.reason)
            raise

    @staticmethod
    def start_process(
        process_key: str,
        variables: Dict[str, Any],
        business_key: str = "",
    ) -> str:
        """Start a new process instance.

        Args:
            process_key: BPMN process definition key.
            variables: Camunda process variables dict.
            business_key: External business key (e.g., case UUID).

        Returns:
            str: The process instance ID.
        """
        payload = {
            "variables": {
                k: {"value": v, "type": "String" if isinstance(v, str) else "Integer"}
                for k, v in variables.items()
            },
        }
        if business_key:
            payload["businessKey"] = business_key

        result = CamundaClient._request(
            "POST", f"/process-definition/key/{process_key}/start", payload
        )
        instance_id = result.get("id", "")
        logger.info("Started Camunda process %s: %s", process_key, instance_id)
        return instance_id

    @staticmethod
    def complete_task(task_id: str, variables: Optional[Dict[str, Any]] = None):
        """Complete a user task and optionally set variables."""
        payload = {}
        if variables:
            payload["variables"] = {
                k: {"value": v, "type": "String" if isinstance(v, str) else "Integer"}
                for k, v in variables.items()
            }

        CamundaClient._request("POST", f"/task/{task_id}/complete", payload)
        logger.info("Completed Camunda task %s", task_id)

    @staticmethod
    def get_tasks_by_process(process_instance_id: str) -> list:
        """Fetch active tasks for a process instance."""
        result = CamundaClient._request(
            "GET", f"/task?processInstanceId={process_instance_id}"
        )
        return result if isinstance(result, list) else []

    @staticmethod
    def get_process_status(process_instance_id: str) -> str:
        """Check if a process instance is still active."""
        try:
            result = CamundaClient._request(
                "GET", f"/history/process-instance/{process_instance_id}"
            )
            return result.get("state", "unknown")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return "not_found"
            raise
