from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    GeoHotspotsListResponse,
    GeoHotspotsResponse,
    HeatmapDataResponse,
    LgaBoundariesResponse,
    LgaDetailResponse,
    NearbyResponse,
)
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.gis.db.models.functions import Centroid, Area
from django.contrib.gis.geos import Point
from .models import LGABoundary, Hotspot
from .serializers import LGABoundarySerializer, HotspotSerializer, HotspotListSerializer

@extend_schema(responses=LgaBoundariesResponse, tags=["Geo"], summary="LGA boundaries")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_lga_boundaries(request):
    """Return all LGA boundaries as GeoJSON FeatureCollection."""
    boundaries = LGABoundary.objects.all()
    serializer = LGABoundarySerializer(boundaries, many=True)
    return Response({
        'type': 'FeatureCollection',
        'features': serializer.data
    })

@extend_schema(responses=LgaDetailResponse, tags=["Geo"], summary="LGA detail")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_lga_detail(request, lga_id):
    """Return single LGA boundary with stats."""
    try:
        boundary = LGABoundary.objects.get(lga_id=lga_id)
        serializer = LGABoundarySerializer(boundary)
        return Response(serializer.data)
    except LGABoundary.DoesNotExist:
        return Response({'error': 'LGA boundary not found'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(responses=GeoHotspotsResponse, tags=["Geo"], summary="Geo hotspots")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_hotspots(request):
    """Return all hotspots as GeoJSON."""
    hotspots = Hotspot.objects.filter(is_active=True)
    serializer = HotspotSerializer(hotspots, many=True)
    return Response({
        'type': 'FeatureCollection',
        'features': serializer.data
    })

@extend_schema(responses=GeoHotspotsListResponse, tags=["Geo"], summary="List geo hotspots")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_hotspots_list(request):
    """Return hotspots as simple list (lat/lng for map markers)."""
    hotspots = Hotspot.objects.filter(is_active=True)
    serializer = HotspotListSerializer(hotspots, many=True)
    return Response(serializer.data)

@extend_schema(responses=HeatmapDataResponse, tags=["Geo"], summary="Heatmap data")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_heatmap_data(request):
    """Return heatmap data: migrant density per LGA."""
    from abia.accounts.models import LGA
    from abia.migrants.models import Migrant
    from django.db.models import Count

    lga_data = []
    for lga in LGA.objects.all():
        count = Migrant.objects.filter(current_lga=lga).count()
        if count > 0:
            boundary = getattr(lga, 'boundary', None)
            if boundary and boundary.centroid:
                lga_data.append({
                    'lga_id': str(lga.id),
                    'name': lga.name,
                    'lat': boundary.centroid.y,
                    'lng': boundary.centroid.x,
                    'density': count,
                    'intensity': min(count / 100, 1.0),
                })
    return Response({
        'type': 'heatmap',
        'max_intensity': max((d['intensity'] for d in lga_data), default=0),
        'points': lga_data
    })

@extend_schema(responses=NearbyResponse, tags=["Geo"], summary="Nearby locations")
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def geo_nearby(request):
    """Find hotspots/migrants near a point."""
    lat = float(request.query_params.get('lat', 0))
    lng = float(request.query_params.get('lng', 0))
    radius_km = float(request.query_params.get('radius', 10))

    point = Point(lng, lat, srid=4326)
    hotspots = Hotspot.objects.filter(
        location__distance_lte=(point, radius_km * 1000)
    ).distance(point).order_by('distance')

    serializer = HotspotListSerializer(hotspots, many=True)
    return Response({
        'center': {'lat': lat, 'lng': lng},
        'radius_km': radius_km,
        'hotspots': serializer.data
    })


# Propagate _spectacular metadata for drf-spectacular
if hasattr(geo_lga_boundaries, '_spectacular') and hasattr(geo_lga_boundaries, 'cls'):
    geo_lga_boundaries.cls._spectacular = geo_lga_boundaries._spectacular
if hasattr(geo_lga_detail, '_spectacular') and hasattr(geo_lga_detail, 'cls'):
    geo_lga_detail.cls._spectacular = geo_lga_detail._spectacular
if hasattr(geo_hotspots, '_spectacular') and hasattr(geo_hotspots, 'cls'):
    geo_hotspots.cls._spectacular = geo_hotspots._spectacular
if hasattr(geo_hotspots_list, '_spectacular') and hasattr(geo_hotspots_list, 'cls'):
    geo_hotspots_list.cls._spectacular = geo_hotspots_list._spectacular
if hasattr(geo_heatmap_data, '_spectacular') and hasattr(geo_heatmap_data, 'cls'):
    geo_heatmap_data.cls._spectacular = geo_heatmap_data._spectacular
if hasattr(geo_nearby, '_spectacular') and hasattr(geo_nearby, 'cls'):
    geo_nearby.cls._spectacular = geo_nearby._spectacular
