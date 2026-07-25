from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    IndicatorTrendResponse,
    MigrationIndicatorsResponse,
    RemittanceIndicatorsResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import WBIndicator, WBDataPoint, WBConfiguration
from .services import WorldBankService
from .serializers import WBIndicatorSerializer, WBDataPointSerializer, WBConfigurationSerializer

class WBIndicatorViewSet(viewsets.ModelViewSet):
    serializer_class = WBIndicatorSerializer
    permission_classes = [IsAuthenticated]
    queryset = WBIndicator.objects.filter(is_active=True)

class WBDataPointViewSet(viewsets.ModelViewSet):
    serializer_class = WBDataPointSerializer
    permission_classes = [IsAuthenticated]
    queryset = WBDataPoint.objects.all()

class WBConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = WBConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WBConfiguration.objects.all()

@extend_schema(responses=IndicatorTrendResponse, tags=["World Bank"], summary="World Bank indicator trend over time")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def indicator_trend(request, indicator_code):
    country = request.query_params.get("country", "NGA")
    return Response({"indicator": indicator_code, "country": country,
                     "data": WorldBankService.get_indicator_trend(indicator_code, country)})

@extend_schema(responses=MigrationIndicatorsResponse, tags=["World Bank"], summary="Migration indicators from World Bank")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_indicators(request):
    return Response({"indicators": WorldBankService.get_migration_indicators()})

@extend_schema(responses=RemittanceIndicatorsResponse, tags=["World Bank"], summary="Remittance indicators from World Bank")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_indicators(request):
    return Response({"indicators": WorldBankService.get_remittance_indicators()})


# Propagate _spectacular metadata for drf-spectacular
if hasattr(indicator_trend, '_spectacular') and hasattr(indicator_trend, 'cls'):
    indicator_trend.cls._spectacular = indicator_trend._spectacular
if hasattr(migration_indicators, '_spectacular') and hasattr(migration_indicators, 'cls'):
    migration_indicators.cls._spectacular = migration_indicators._spectacular
if hasattr(remittance_indicators, '_spectacular') and hasattr(remittance_indicators, 'cls'):
    remittance_indicators.cls._spectacular = remittance_indicators._spectacular
