import uuid

from django.conf import settings
from django.db import models


class Referral(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(
        "cases.Case", on_delete=models.CASCADE, related_name="referrals"
    )
    from_lga = models.ForeignKey(
        "accounts.LGA", on_delete=models.PROTECT, related_name="referrals_sent"
    )
    to_lga = models.ForeignKey(
        "accounts.LGA", on_delete=models.PROTECT, related_name="referrals_received"
    )
    to_organization = models.CharField(max_length=200, blank=True)
    to_contact_name = models.CharField(max_length=200, blank=True)
    to_contact_phone = models.CharField(max_length=20, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    camunda_process_id = models.CharField(max_length=100, blank=True)
    documents = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="referrals_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if self.from_lga_id and self.to_lga_id and self.from_lga_id == self.to_lga_id:
            raise ValidationError({"to_lga": "Referral cannot be to the same LGA."})
        if not self.case_id:
            raise ValidationError({"case": "Case is required."})

    class Meta:
        app_label = "referrals"
        ordering = ["-created_at"]
