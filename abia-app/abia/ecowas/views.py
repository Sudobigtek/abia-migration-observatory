from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import ECOWASMigrantFlow, ECOWASTradeFlow, ECOWASConfiguration
from .services import ECOWASService
from .serializers import ECOWASMigrantFlowSerializer, ECOWASTradeFlowSerializer, ECOWASConfigurationSerializer

class ECOWASMigrantFlowViewSet(viewsets.ModelViewSet):
    serializer_class = ECOWASMigrantFlowSerializer
    permission_classes = [IsAuthenticated]
    queryset = ECOWASMigrantFlow.objects.all()

class ECOWASTradeFlowViewSet(viewsets.ModelViewSet):
    serializer_class = ECOWASTradeFlowSerializer
    permission_classes = [IsAuthenticated]
    queryset = ECOWASTradeFlow.objects.all()

class ECOWASConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = ECOWASConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ECOWASConfiguration.objects.all()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_corridors(request):
    return Response({"corridors": ECOWASService.get_migration_by_corridor()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_by_sector(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": ECOWASService.get_migration_by_sector(year)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def free_movement_stats(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response(ECOWASService.get_free_movement_stats(year))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def intra_regional_trade(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response(ECOWASService.get_intra_regional_trade(year))