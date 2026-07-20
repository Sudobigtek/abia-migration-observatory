import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model

User = get_user_model()

class MapLayer(models.Model):
    LAYER_TYPES = [
        ("lga_boundary", "LGA Boundary"),
        ("migrant_cluster", "Migrant Cluster"),
        ("case_hotspot", "Case Hotspot"),
        ("referral_route", "Referral Route"),
        ("custom", "Custom Layer"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    layer_type = models.CharField(max_length=20, choices=LAYER_TYPES)
    description = models.TextField(blank=True)
    geojson_data = models.JSONField(default=dict, help_text="GeoJSON FeatureCollection")
    style_config = models.JSONField(default=dict, blank=True, help_text="Leaflet style options")
    is_visible = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    z_index = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["z_index", "-created_at"]

    def __str__(self):
        return self.name