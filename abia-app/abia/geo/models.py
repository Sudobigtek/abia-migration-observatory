import uuid
from django.db import models
from django.db import models as gis_models  # TEMP: GIS disabled for SQLite

class LGABoundary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lga = models.OneToOneField('accounts.LGA', on_delete=models.CASCADE, related_name='geo_boundary')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    geometry = models.TextField()
    centroid = models.CharField(max_length=255, blank=True, null=True)  # was PointField
    area_sqkm = models.FloatField(null=True, blank=True)
    population_estimate = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'LGA Boundary'
        verbose_name_plural = 'LGA Boundaries'

    def __str__(self):
        return self.name

class Hotspot(models.Model):
    HOTSPOT_TYPES = [
        ('transit', 'Transit Point'),
        ('settlement', 'Settlement'),
        ('camp', 'Camp'),
        ('border', 'Border Crossing'),
        ('service', 'Service Center'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    hotspot_type = models.CharField(max_length=20, choices=HOTSPOT_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)  # was PointField
    lga = models.ForeignKey('accounts.LGA', on_delete=models.CASCADE, related_name='hotspots')
    description = models.TextField(blank=True)
    migrant_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-migrant_count']

    def __str__(self):
        return f"{self.name} ({self.hotspot_type})"
