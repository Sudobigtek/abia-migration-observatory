from django.contrib.gis.geos import Point, Polygon
from .models import MapLayer

class MapService:
    @staticmethod
    def get_lga_boundaries_geojson():
        from accounts.models import LGA
        features = []
        for lga in LGA.objects.all():
            if lga.boundary:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": lga.boundary.coords
                    },
                    "properties": {
                        "name": lga.name,
                        "id": str(lga.id),
                        "migrant_count": getattr(lga, "migrant_count", 0)
                    }
                })
        return {"type": "FeatureCollection", "features": features}

    @staticmethod
    def get_migrant_clusters():
        from abia.migrants.models import Migrant
        from django.db.models import Count
        data = Migrant.objects.values("current_lga__name").annotate(
            count=Count("id")
        ).order_by("-count")
        features = []
        for d in data:
            if d["current_lga__name"]:
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "lga": d["current_lga__name"],
                        "count": d["count"]
                    }
                })
        return {"type": "FeatureCollection", "features": features}

    @staticmethod
    def get_hotspot_layer():
        from abia.hotspot.models import HotspotPrediction
        predictions = HotspotPrediction.objects.select_related("lga").filter(risk_level__in=["high", "critical"])
        features = []
        for p in predictions:
            if p.centroid:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [p.centroid.x, p.centroid.y]
                    },
                    "properties": {
                        "lga": str(p.lga),
                        "risk_level": p.risk_level,
                        "risk_score": p.risk_score,
                        "predicted_count": p.predicted_migrant_count
                    }
                })
        return {"type": "FeatureCollection", "features": features}

    @staticmethod
    def build_map_data():
        return {
            "layers": [
                {"name": "LGA Boundaries", "type": "lga_boundary", "data": MapService.get_lga_boundaries_geojson()},
                {"name": "Migrant Clusters", "type": "migrant_cluster", "data": MapService.get_migrant_clusters()},
                {"name": "Hotspots", "type": "case_hotspot", "data": MapService.get_hotspot_layer()},
            ]
        }