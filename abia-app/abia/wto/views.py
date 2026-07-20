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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trade_balance(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": WTOService.get_trade_balance_by_sector(year)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_partners(request):
    flow = request.query_params.get("flow", "export")
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"partners": WTOService.get_top_partners(flow, year)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def labour_intensive_trade(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": WTOService.get_labour_intensive_trade(year)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def yearly_summary(request):
    return Response({"years": WTOService.get_yearly_summary()})