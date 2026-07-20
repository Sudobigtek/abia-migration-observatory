from rest_framework import serializers
from .models import MapLayer

class MapLayerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    class Meta:
        model = MapLayer
        fields = ["id", "name", "layer_type", "description", "geojson_data", "style_config",
                  "is_visible", "is_public", "z_index", "created_by", "created_by_name",
                  "created_at", "updated_at"]