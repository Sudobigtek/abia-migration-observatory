import uuid
from django.db import models

class TradeRecord(models.Model):
    FLOW_CHOICES = [
        ("export", "Export"),
        ("import", "Import"),
        ("re_export", "Re-Export"),
    ]
    SECTOR_CHOICES = [
        ("agriculture", "Agriculture"),
        ("manufacturing", "Manufacturing"),
        ("mining", "Mining"),
        ("services", "Services"),
        ("textiles", "Textiles"),
        ("technology", "Technology"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow_type = models.CharField(max_length=20, choices=FLOW_CHOICES)
    product_category = models.CharField(max_length=100)
    hs_code = models.CharField(max_length=20, blank=True)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default="manufacturing")
    value_usd = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity_unit = models.CharField(max_length=20, blank=True)
    trade_partner = models.CharField(max_length=100)
    partner_country_code = models.CharField(max_length=10)
    reporter_country = models.CharField(max_length=100, default="Nigeria")
    year = models.PositiveIntegerField()
    quarter = models.PositiveIntegerField(null=True, blank=True)
    labour_intensity_score = models.PositiveIntegerField(default=0, help_text="0-100 estimate of labour intensity")
    data_source = models.CharField(max_length=50, default="WTO")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-value_usd"]
        indexes = [
            models.Index(fields=["sector", "-year"]),
            models.Index(fields=["flow_type", "-year"]),
            models.Index(fields=["trade_partner", "-year"]),
        ]

    def __str__(self):
        return f"{self.flow_type} {self.product_category} {self.year} ({self.value_usd} USD)"

class WTOConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_base_url = models.URLField(default="https://api.wto.org/timeseries/v1")
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    auto_sync_enabled = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WTO Config ({self.api_base_url})"