import uuid
from django.db import models

class WBIndicator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    indicator_code = models.CharField(max_length=50, unique=True)
    indicator_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default="general")
    unit = models.CharField(max_length=50, blank=True)
    source_note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["indicator_code"]

    def __str__(self):
        return f"{self.indicator_code} - {self.indicator_name}"

class WBDataPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    indicator = models.ForeignKey(WBIndicator, on_delete=models.CASCADE, related_name="data_points")
    country_code = models.CharField(max_length=10)
    country_name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year"]
        unique_together = [["indicator", "country_code", "year"]]
        indexes = [
            models.Index(fields=["indicator", "country_code", "-year"]),
        ]

    def __str__(self):
        return f"{self.indicator.indicator_code} {self.country_code} {self.year}: {self.value}"

class WBConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_base_url = models.URLField(default="https://api.worldbank.org/v2")
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"World Bank Config ({self.api_base_url})"