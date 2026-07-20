import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RemittanceRecord(models.Model):
    CHANNEL_CHOICES = [
        ("bank", "Bank Transfer"),
        ("mto", "Money Transfer Operator"),
        ("crypto", "Cryptocurrency"),
        ("informal", "Informal / Hawala"),
        ("mobile", "Mobile Money"),
    ]
    PURPOSE_CHOICES = [
        ("family_support", "Family Support"),
        ("business", "Business Investment"),
        ("education", "Education"),
        ("healthcare", "Healthcare"),
        ("real_estate", "Real Estate"),
        ("other", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_name = models.CharField(max_length=255)
    sender_country = models.CharField(max_length=100, default="United States")
    sender_currency = models.CharField(max_length=10, default="USD")
    amount_sent = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    naira_equivalent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    recipient_name = models.CharField(max_length=255)
    recipient_lga = models.ForeignKey("accounts.LGA", on_delete=models.SET_NULL, null=True, blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    recipient_account = models.CharField(max_length=50, blank=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="bank")
    bank_name = models.CharField(max_length=100, blank=True)
    transaction_reference = models.CharField(max_length=100, unique=True)
    transaction_date = models.DateTimeField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="family_support")
    status = models.CharField(max_length=20, default="completed")
    verified_by_cbn = models.BooleanField(default=False)
    cbn_reference = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["recipient_lga", "-transaction_date"]),
            models.Index(fields=["channel", "-transaction_date"]),
            models.Index(fields=["status", "-transaction_date"]),
        ]

    def __str__(self):
        return f"{self.sender_name} -> {self.recipient_name} ({self.naira_equivalent} NGN)"

class CBNConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_base_url = models.URLField(default="https://api.cbn.gov.ng/v1")
    api_key = models.CharField(max_length=255, blank=True)
    client_id = models.CharField(max_length=100, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CBN Config ({self.api_base_url})"