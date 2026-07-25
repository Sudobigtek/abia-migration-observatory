from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    HotspotListResponse,
    MapDataResponse,
    TriggerAnalysisResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import HotspotService
from .models import HotspotPrediction
from .serializers import HotspotPredictionSerializer

@extend_schema(responses=MapDataResponse, tags=["Hotspots"], summary="Map data")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def map_data(request):
    geojson = HotspotService.get_geojson_hotspots()
    return Response(geojson)

@extend_schema(responses=TriggerAnalysisResponse, tags=["Hotspots"], summary="Trigger hotspot analysis")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_analysis(request):
    period_days = request.data.get("period_days", 90)
    predictions = HotspotService.analyze_hotspots(period_days)
    return Response({
        "status": "completed",
        "predictions_generated": len(predictions),
        "period_days": period_days
    })


trigger_analysis.cls.serializer_class = TriggerAnalysisResponse
@extend_schema(responses=HotspotListResponse, tags=["Hotspots"], summary="List hotspots")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hotspot_list(request):
    predictions = HotspotPrediction.objects.select_related("lga").order_by("-risk_score")[:50]
    serializer = HotspotPredictionSerializer(predictions, many=True)
    return Response(serializer.data)


# Propagate _spectacular metadata for drf-spectacular
if hasattr(map_data, '_spectacular') and hasattr(map_data, 'cls'):
    map_data.cls._spectacular = map_data._spectacular
if hasattr(trigger_analysis, '_spectacular') and hasattr(trigger_analysis, 'cls'):
    trigger_analysis.cls._spectacular = trigger_analysis._spectacular
if hasattr(hotspot_list, '_spectacular') and hasattr(hotspot_list, 'cls'):
    hotspot_list.cls._spectacular = hotspot_list._spectacular
