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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def indicator_trend(request, indicator_code):
    country = request.query_params.get("country", "NGA")
    return Response({"indicator": indicator_code, "country": country,
                     "data": WorldBankService.get_indicator_trend(indicator_code, country)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_indicators(request):
    return Response({"indicators": WorldBankService.get_migration_indicators()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_indicators(request):
    return Response({"indicators": WorldBankService.get_remittance_indicators()})