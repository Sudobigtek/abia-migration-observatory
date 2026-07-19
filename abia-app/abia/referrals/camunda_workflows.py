"""Referral workflows via Camunda.

Per Architecture Contract §2.3.
"""

import logging

from abia.common.camunda_client import CamundaClient

logger = logging.getLogger("abia.referrals.workflow")

PROCESS_KEY = "referral-process"


class ReferralWorkflowService:
    """Orchestrate inter-LGA referral via Camunda."""

    @staticmethod
    def start_referral_workflow(
        referral_id: str,
        from_lga_id: str,
        to_lga_id: str,
        reason: str,
    ) -> str:
        """Start a new referral workflow.

        Args:
            referral_id: UUID of the Referral.
            from_lga_id: Source LGA ID.
            to_lga_id: Destination LGA ID.
            reason: Referral reason text.

        Returns:
            str: Camunda process instance ID.
        """
        return CamundaClient.start_process(
            PROCESS_KEY,
            variables={
                "referralId": str(referral_id),
                "fromLgaId": str(from_lga_id),
                "toLgaId": str(to_lga_id),
                "reason": reason,
            },
            business_key=str(referral_id),
        )

    @staticmethod
    def approve_referral(task_id: str, approved_by: str):
        """Approve a pending referral."""
        CamundaClient.complete_task(task_id, {"approvedBy": approved_by})

    @staticmethod
    def mark_in_transit(task_id: str, transport_mode: str = ""):
        """Mark referral as in transit."""
        CamundaClient.complete_task(task_id, {"transportMode": transport_mode})
