"""Geo report engine for spatial data export."""
from typing import Dict, Any, List
import json


class GeoEngine:
    """Generate GeoJSON / Shapefile exports from spatial querysets."""

    @staticmethod
    def to_geojson(features: List[Dict[str, Any]]) -> str:
        """Convert feature list to GeoJSON FeatureCollection."""
        collection = {
            "type": "FeatureCollection",
            "features": features,
        }
        return json.dumps(collection, indent=2)
