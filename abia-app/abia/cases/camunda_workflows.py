"""Case management workflows via Camunda.

Per Architecture Contract §2.3 and §16.
"""

import logging

from abia.common.camunda_client import CamundaClient

logger = logging.getLogger("abia.cases.workflow")

PROCESS_KEY = "case-management-process"


class CaseWorkflowService:
    """Orchestrate case lifecycle via Camunda."""

    @staticmethod
    def start_case_workflow(case_id: str, officer_id: str, priority: str) -> str:
        """Start a new case workflow instance.

        Args:
            case_id: UUID of the Case.
            officer_id: ID of the assigned field officer.
            priority: low, medium, high, critical.

        Returns:
            str: Camunda process instance ID.
        """
        return CamundaClient.start_process(
            PROCESS_KEY,
            variables={
                "caseId": str(case_id),
                "officerId": str(officer_id),
                "priority": priority,
            },
            business_key=str(case_id),
        )

    @staticmethod
    def get_case_tasks(case_id: str) -> list:
        """Fetch active tasks for a case."""
        # In production, query by businessKey or process variable
        # For dev, return empty list if Camunda is not running
        try:
            tasks = CamundaClient._request(
                "GET", f"/task?processInstanceBusinessKey={case_id}"
            )
            return tasks if isinstance(tasks, list) else []
        except Exception:
            logger.warning("Camunda unreachable, returning empty task list")
            return []

    @staticmethod
    def complete_intake_task(task_id: str, notes: str = ""):
        """Complete the initial intake task."""
        CamundaClient.complete_task(task_id, {"intakeNotes": notes})
