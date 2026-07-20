import uuid
from django.db import models

class AthleteProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    SPORT_CHOICES = [
        ("football", "Football"),
        ("basketball", "Basketball"),
        ("athletics", "Athletics"),
        ("boxing", "Boxing"),
        ("tennis", "Tennis"),
        ("cricket", "Cricket"),
        ("rugby", "Rugby"),
        ("other", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, default="Nigeria")
    origin_lga = models.ForeignKey("accounts.LGA", on_delete=models.SET_NULL, null=True, blank=True)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES, default="football")
    position = models.CharField(max_length=50, blank=True)
    current_club = models.CharField(max_length=255, blank=True)
    current_country = models.CharField(max_length=100, blank=True)
    market_value_usd = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["sport", "origin_lga"]),
            models.Index(fields=["nationality", "is_active"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.sport})"

class AthleteTransfer(models.Model):
    TRANSFER_TYPES = [
        ("permanent", "Permanent Transfer"),
        ("loan", "Loan"),
        ("free_transfer", "Free Transfer"),
        ("youth_promotion", "Youth Promotion"),
        ("return", "Return from Abroad"),
    ]
    STATUS_CHOICES = [
        ("rumoured", "Rumoured"),
        ("negotiating", "Negotiating"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name="transfers")
    from_club = models.CharField(max_length=255)
    from_country = models.CharField(max_length=100)
    to_club = models.CharField(max_length=255)
    to_country = models.CharField(max_length=100)
    transfer_fee_usd = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPES, default="permanent")
    transfer_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    agent_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    is_international = models.BooleanField(default=False, help_text="Cross-border transfer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transfer_date"]
        indexes = [
            models.Index(fields=["athlete", "-transfer_date"]),
            models.Index(fields=["to_country", "-transfer_date"]),
            models.Index(fields=["is_international", "-transfer_date"]),
        ]

    def __str__(self):
        return f"{self.athlete.full_name}: {self.from_club} -> {self.to_club}"

class SportsConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source_name = models.CharField(max_length=100, default="Transfermarkt API")
    api_base_url = models.URLField(default="https://api.transfermarkt.com/v1")
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sports Config ({self.data_source_name})"