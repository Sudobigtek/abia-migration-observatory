from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    LabourIntensiveTradeResponse,
    TopPartnersResponse,
    TradeBalanceResponse,
    YearlySummaryResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import TradeRecord, WTOConfiguration
from .services import WTOService
from .serializers import TradeRecordSerializer, WTOConfigurationSerializer

class TradeRecordViewSet(viewsets.ModelViewSet):
    serializer_class = TradeRecordSerializer
    permission_classes = [IsAuthenticated]
    queryset = TradeRecord.objects.all()

class WTOConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = WTOConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = WTOConfiguration.objects.all()

@extend_schema(responses=TradeBalanceResponse, tags=["WTO"], summary="Trade balance indicators")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trade_balance(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": WTOService.get_trade_balance_by_sector(year)})

@extend_schema(responses=TopPartnersResponse, tags=["WTO"], summary="Top trading partners")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_partners(request):
    flow = request.query_params.get("flow", "export")
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"partners": WTOService.get_top_partners(flow, year)})

@extend_schema(responses=LabourIntensiveTradeResponse, tags=["WTO"], summary="Labour-intensive trade data")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def labour_intensive_trade(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": WTOService.get_labour_intensive_trade(year)})

@extend_schema(responses=YearlySummaryResponse, tags=["WTO"], summary="Yearly trade summary")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def yearly_summary(request):
    return Response({"years": WTOService.get_yearly_summary()})


# Propagate _spectacular metadata for drf-spectacular
if hasattr(trade_balance, '_spectacular') and hasattr(trade_balance, 'cls'):
    trade_balance.cls._spectacular = trade_balance._spectacular
if hasattr(top_partners, '_spectacular') and hasattr(top_partners, 'cls'):
    top_partners.cls._spectacular = top_partners._spectacular
if hasattr(labour_intensive_trade, '_spectacular') and hasattr(labour_intensive_trade, 'cls'):
    labour_intensive_trade.cls._spectacular = labour_intensive_trade._spectacular
if hasattr(yearly_summary, '_spectacular') and hasattr(yearly_summary, 'cls'):
    yearly_summary.cls._spectacular = yearly_summary._spectacular
