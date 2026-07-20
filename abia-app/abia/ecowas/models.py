import uuid
from django.db import models

class ECOWASMigrantFlow(models.Model):
    MIGRATION_TYPES = [
        ("labour", "Labour Migration"),
        ("forced", "Forced Migration"),
        ("irregular", "Irregular Migration"),
        ("student", "Student Migration"),
        ("trade", "Trade-Related Movement"),
    ]
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_of_origin = models.CharField(max_length=100)
    country_of_destination = models.CharField(max_length=100)
    migration_type = models.CharField(max_length=20, choices=MIGRATION_TYPES, default="labour")
    sector = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    age_group = models.CharField(max_length=20, blank=True)
    estimated_count = models.PositiveIntegerField(default=0)
    year = models.PositiveIntegerField()
    protocol_article = models.CharField(max_length=50, blank=True, help_text="ECOWAS Free Movement Protocol article")
    data_source = models.CharField(max_length=50, default="ECOWAS Commission")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-estimated_count"]
        indexes = [
            models.Index(fields=["country_of_origin", "-year"]),
            models.Index(fields=["migration_type", "-year"]),
            models.Index(fields=["sector", "-year"]),
        ]

    def __str__(self):
        return f"{self.country_of_origin} -> {self.country_of_destination} ({self.estimated_count})"

class ECOWASTradeFlow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter_country = models.CharField(max_length=100)
    partner_country = models.CharField(max_length=100)
    product_category = models.CharField(max_length=100)
    export_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    import_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    year = models.PositiveIntegerField()
    data_source = models.CharField(max_length=50, default="ECOWAS Trade Observatory")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year"]
        indexes = [
            models.Index(fields=["reporter_country", "partner_country", "-year"]),
        ]

    def __str__(self):
        return f"{self.reporter_country} <-> {self.partner_country} {self.year}"

class ECOWASConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_base_url = models.URLField(default="https://ecowas.int/api/v1")
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ECOWAS Config ({self.api_base_url})"