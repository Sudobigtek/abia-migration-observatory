from typing import Any

from django.db import transaction

from .models import Referral


class ReferralRepository:
    """Data access layer for Referral entities."""

    @staticmethod
    def get_all() -> Any:
        """Return all referrals with related data."""
        return (
            Referral.objects.select_related("case", "from_lga", "to_lga")
            .order_by("-created_at")
            .all()
        )

    @staticmethod
    def get_by_id(referral_id: int) -> Any:
        """Return a referral by ID or None."""
        return Referral.objects.filter(id=referral_id).first()

    @staticmethod
    def get_by_lga(lga_id: int) -> Any:
        """Return referrals filtered by originating LGA."""
        return Referral.objects.filter(from_lga_id=lga_id).order_by("-created_at")

    @staticmethod
    def get_by_case(case_id: int) -> Any:
        """Return referrals for a specific case."""
        return Referral.objects.filter(case_id=case_id).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create(data: dict) -> Any:
        """Create a new referral."""
        return Referral.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(referral_id: int, data: dict) -> Any:
        """Update an existing referral."""
        Referral.objects.filter(id=referral_id).update(**data)
        return Referral.objects.filter(id=referral_id).first()

    @staticmethod
    @transaction.atomic
    def delete(referral_id: int) -> None:
        """Delete a referral by ID."""
        Referral.objects.filter(id=referral_id).delete()
