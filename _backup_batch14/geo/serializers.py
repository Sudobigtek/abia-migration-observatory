from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import LGABoundary, Hotspot

class LGABoundarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = LGABoundary
        geo_field = 'geometry'
        fields = ['id', 'name', 'code', 'lga', 'area_sqkm', 'population_estimate', 'created_at']

class HotspotSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Hotspot
        geo_field = 'location'
        fields = ['id', 'name', 'hotspot_type', 'lga', 'description', 'migrant_count', 'is_active', 'created_at']

class HotspotListSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='location.y', read_only=True)
    lng = serializers.FloatField(source='location.x', read_only=True)

    class Meta:
        model = Hotspot
        fields = ['id', 'name', 'hotspot_type', 'lat', 'lng', 'migrant_count', 'is_active']
