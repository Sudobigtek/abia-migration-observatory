from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import GIZDataExchange, GIZIndicator
from .services import GIZService
from .serializers import GIZDataExchangeSerializer, GIZIndicatorSerializer

class GIZDataExchangeViewSet(viewsets.ModelViewSet):
    serializer_class = GIZDataExchangeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return GIZDataExchange.objects.all()
        return GIZDataExchange.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class GIZIndicatorViewSet(viewsets.ModelViewSet):
    serializer_class = GIZIndicatorSerializer
    permission_classes = [IsAuthenticated]
    queryset = GIZIndicator.objects.filter(is_active=True)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def giz_reports(request):
    return Response({
        "reports": [
            {"id": "migration_governance", "name": "Migration Governance Report", "url": "/api/v1/giz/reports/migration-governance/"},
            {"id": "reintegration", "name": "Reintegration Report", "url": "/api/v1/giz/reports/reintegration/"},
            {"id": "protection", "name": "Protection & Assistance Report", "url": "/api/v1/giz/reports/protection/"},
        ]
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_governance_report(request):
    return Response(GIZService.build_migration_governance_report())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reintegration_report(request):
    return Response(GIZService.build_reintegration_report())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protection_report(request):
    return Response(GIZService.build_protection_report())

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_report(request, exchange_id):
    exchange = GIZService.submit_to_giz(exchange_id)
    return Response({"status": "submitted", "id": str(exchange.id), "submitted_at": exchange.submitted_at})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refresh_indicators(request):
    data = GIZService.update_indicators_from_data()
    return Response({"status": "refreshed", "indicators": data})