from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    HotspotMapResponse,
    LGABoundariesResponse,
    MapConfigResponse,
    MapDataResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MapLayer
from .services import MapService
from .serializers import MapLayerSerializer

class MapLayerViewSet(viewsets.ModelViewSet):
    serializer_class = MapLayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MapLayer.objects.all()
        return MapLayer.objects.filter(created_by=user) | MapLayer.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@extend_schema(responses=MapDataResponse, tags=["Maps"], summary="Map data")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def map_data(request):
    return Response(MapService.build_map_data())

@extend_schema(responses=LGABoundariesResponse, tags=["Maps"], summary="LGA boundaries")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lga_boundaries(request):
    return Response(MapService.get_lga_boundaries_geojson())

@extend_schema(responses=HotspotMapResponse, tags=["Maps"], summary="Hotspot map")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hotspot_map(request):
    return Response(MapService.get_hotspot_layer())

@extend_schema(responses=MapConfigResponse, tags=["Maps"], summary="Map config")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def map_config(request):
    return Response({
        "center": {"lat": 5.45, "lng": 7.5},
        "zoom": 10,
        "max_zoom": 18,
        "tile_url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "&copy; OpenStreetMap contributors",
        "layers": [
            {"id": "lga", "name": "LGA Boundaries", "visible": True, "color": "#3388ff"},
            {"id": "clusters", "name": "Migrant Clusters", "visible": True, "color": "#28a745"},
            {"id": "hotspots", "name": "Hotspots", "visible": True, "color": "#dc3545"},
        ]
    })


# Propagate _spectacular metadata for drf-spectacular
if hasattr(map_data, '_spectacular') and hasattr(map_data, 'cls'):
    map_data.cls._spectacular = map_data._spectacular
if hasattr(lga_boundaries, '_spectacular') and hasattr(lga_boundaries, 'cls'):
    lga_boundaries.cls._spectacular = lga_boundaries._spectacular
if hasattr(hotspot_map, '_spectacular') and hasattr(hotspot_map, 'cls'):
    hotspot_map.cls._spectacular = hotspot_map._spectacular
if hasattr(map_config, '_spectacular') and hasattr(map_config, 'cls'):
    map_config.cls._spectacular = map_config._spectacular
