"""Tests for Camunda referral workflows."""

import pytest
from unittest.mock import patch

from abia.referrals.camunda_workflows import ReferralWorkflowService


class TestReferralWorkflowService:
    """Test referral workflow orchestration."""

    @patch("abia.referrals.camunda_workflows.CamundaClient.start_process")
    def test_start_referral_workflow(self, mock_start):
        """Given referral data, start Camunda process."""
        mock_start.return_value = "ref-proc-456"

        result = ReferralWorkflowService.start_referral_workflow(
            referral_id="ref-uuid",
            from_lga_id="lga-1",
            to_lga_id="lga-2",
            reason="Medical emergency",
        )

        assert result == "ref-proc-456"
        mock_start.assert_called_once()
        args, kwargs = mock_start.call_args
        assert args[0] == "referral-process"
        assert kwargs["variables"]["reason"] == "Medical emergency"

    @patch("abia.referrals.camunda_workflows.CamundaClient.complete_task")
    def test_approve_referral(self, mock_complete):
        """Given task ID, approve referral."""
        ReferralWorkflowService.approve_referral("task-3", "coordinator-1")

        mock_complete.assert_called_once_with("task-3", {"approvedBy": "coordinator-1"})

    @patch("abia.referrals.camunda_workflows.CamundaClient.complete_task")
    def test_mark_in_transit(self, mock_complete):
        """Given task ID, mark in transit."""
        ReferralWorkflowService.mark_in_transit("task-4", "ambulance")

        mock_complete.assert_called_once_with("task-4", {"transportMode": "ambulance"})

    @patch("abia.referrals.camunda_workflows.CamundaClient.start_process")
    def test_start_referral_workflow_error(self, mock_start):
        """Given Camunda error, raise exception."""
        from urllib.error import URLError
        mock_start.side_effect = URLError("Connection refused")

        with pytest.raises(URLError):
            ReferralWorkflowService.start_referral_workflow(
                "ref-uuid", "lga-1", "lga-2", "reason"
            )
