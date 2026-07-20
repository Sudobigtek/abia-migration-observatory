from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChartDashboard
from .services import ChartService
from .serializers import ChartDashboardSerializer

class ChartDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = ChartDashboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ChartDashboard.objects.all()
        return ChartDashboard.objects.filter(created_by=user) | ChartDashboard.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_data(request, dashboard_id):
    from django.shortcuts import get_object_or_404
    dashboard = get_object_or_404(ChartDashboard, id=dashboard_id)
    data = ChartService.build_chart_data(dashboard)
    return Response({"dashboard": dashboard.name, "chart_type": dashboard.chart_type, "data": data})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def preset_charts(request):
    return Response({
        "presets": [
            # Core Migration
            {"id": "migrants-by-lga", "name": "Migrants by LGA", "type": "bar", "source": "migrants"},
            {"id": "cases-by-status", "name": "Cases by Status", "type": "pie", "source": "cases"},
            {"id": "referral-rate", "name": "Referral Completion Rate", "type": "doughnut", "source": "referrals"},
            {"id": "migrant-trends", "name": "Migrant Registration Trends", "type": "line", "source": "trends"},
            # CBN / Remittances
            {"id": "remittances-by-lga", "name": "Remittances by LGA (NGN)", "type": "bar", "source": "remittances_by_lga"},
            {"id": "remittances-by-channel", "name": "Remittances by Channel", "type": "pie", "source": "remittances_by_channel"},
            {"id": "remittance-trends", "name": "Monthly Remittance Trends", "type": "line", "source": "remittance_trends"},
            # WTO / Trade
            {"id": "trade-balance", "name": "Trade Balance by Sector", "type": "bar", "source": "trade_balance"},
            {"id": "labour-intensive-trade", "name": "Labour-Intensive Trade", "type": "bar", "source": "labour_intensive_trade"},
            # ECOWAS
            {"id": "ecowas-corridors", "name": "Top ECOWAS Migration Corridors", "type": "horizontalBar", "source": "ecowas_corridors"},
            {"id": "ecowas-free-movement", "name": "Free Movement by Gender", "type": "doughnut", "source": "ecowas_free_movement"},
            # World Bank
            {"id": "wb-remittance-indicators", "name": "WB Remittance Indicators", "type": "line", "source": "wb_remittance_indicators"},
            # Sports
            {"id": "sports-destinations", "name": "Athlete Transfers by Destination", "type": "bar", "source": "sports_destinations"},
            {"id": "sports-talent-value", "name": "Sports Talent Export Value", "type": "pie", "source": "sports_talent_value"},
            {"id": "sports-lga-map", "name": "Talent Distribution by LGA", "type": "bar", "source": "sports_lga_map"},
        ]
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_summary(request):
    return Response(ChartService.get_unified_summary())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def integration_status(request):
    from abia.cbn.models import CBNConfiguration
    from abia.worldbank.models import WBConfiguration
    from abia.wto.models import WTOConfiguration
    from abia.ecowas.models import ECOWASConfiguration
    from abia.sports.models import SportsConfiguration
    return Response({
        "integrations": {
            "cbn": {"configured": CBNConfiguration.objects.filter(is_active=True).exists()},
            "world_bank": {"configured": WBConfiguration.objects.filter(is_active=True).exists()},
            "wto": {"configured": WTOConfiguration.objects.filter(is_active=True).exists()},
            "ecowas": {"configured": ECOWASConfiguration.objects.filter(is_active=True).exists()},
            "sports": {"configured": SportsConfiguration.objects.filter(is_active=True).exists()},
        }
    })