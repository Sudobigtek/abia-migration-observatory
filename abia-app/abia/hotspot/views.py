from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import HotspotService
from .models import HotspotPrediction
from .serializers import HotspotPredictionSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def map_data(request):
    geojson = HotspotService.get_geojson_hotspots()
    return Response(geojson)

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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hotspot_list(request):
    predictions = HotspotPrediction.objects.select_related("lga").order_by("-risk_score")[:50]
    serializer = HotspotPredictionSerializer(predictions, many=True)
    return Response(serializer.data)