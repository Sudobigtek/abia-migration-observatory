"""Tests for Camunda case workflows."""

import pytest
from unittest.mock import patch, MagicMock

from abia.cases.camunda_workflows import CaseWorkflowService


class TestCaseWorkflowService:
    """Test case workflow orchestration."""

    @patch("abia.cases.camunda_workflows.CamundaClient.start_process")
    def test_start_case_workflow(self, mock_start):
        """Given case data, start Camunda process."""
        mock_start.return_value = "proc-123"

        result = CaseWorkflowService.start_case_workflow(
            case_id="case-uuid",
            officer_id="officer-1",
            priority="high",
        )

        assert result == "proc-123"
        mock_start.assert_called_once()
        args, kwargs = mock_start.call_args
        assert args[0] == "case-management-process"
        assert kwargs["variables"]["caseId"] == "case-uuid"
        assert kwargs["variables"]["priority"] == "high"

    @patch("abia.cases.camunda_workflows.CamundaClient._request")
    def test_get_case_tasks(self, mock_request):
        """Given case ID, fetch active tasks."""
        mock_request.return_value = [
            {"id": "task-1", "name": "Intake"},
            {"id": "task-2", "name": "Review"},
        ]

        tasks = CaseWorkflowService.get_case_tasks("case-uuid")

        assert len(tasks) == 2
        assert tasks[0]["name"] == "Intake"

    @patch("abia.cases.camunda_workflows.CamundaClient._request")
    def test_get_case_tasks_camunda_down(self, mock_request):
        """Given Camunda unreachable, return empty list gracefully."""
        from urllib.error import URLError
        mock_request.side_effect = URLError("Connection refused")

        tasks = CaseWorkflowService.get_case_tasks("case-uuid")

        assert tasks == []

    @patch("abia.cases.camunda_workflows.CamundaClient.complete_task")
    def test_complete_intake_task(self, mock_complete):
        """Given task ID, complete intake."""
        CaseWorkflowService.complete_intake_task("task-1", "Initial notes")

        mock_complete.assert_called_once_with("task-1", {"intakeNotes": "Initial notes"})
