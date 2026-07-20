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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def map_data(request):
    return Response(MapService.build_map_data())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lga_boundaries(request):
    return Response(MapService.get_lga_boundaries_geojson())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hotspot_map(request):
    return Response(MapService.get_hotspot_layer())

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