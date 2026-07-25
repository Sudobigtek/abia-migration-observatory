from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    FreeMovementStatsResponse,
    IntraRegionalTradeResponse,
    MigrationBySectorResponse,
    MigrationCorridorsResponse,
)
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

@extend_schema(responses=MigrationCorridorsResponse, tags=["ECOWAS"], summary="Migration corridors")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_corridors(request):
    return Response({"corridors": ECOWASService.get_migration_by_corridor()})

@extend_schema(responses=MigrationBySectorResponse, tags=["ECOWAS"], summary="Migration by sector")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def migration_by_sector(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response({"sectors": ECOWASService.get_migration_by_sector(year)})

@extend_schema(responses=FreeMovementStatsResponse, tags=["ECOWAS"], summary="Free movement statistics")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def free_movement_stats(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response(ECOWASService.get_free_movement_stats(year))

@extend_schema(responses=IntraRegionalTradeResponse, tags=["ECOWAS"], summary="Intra-regional trade")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def intra_regional_trade(request):
    year = request.query_params.get("year")
    year = int(year) if year else None
    return Response(ECOWASService.get_intra_regional_trade(year))


# Propagate _spectacular metadata for drf-spectacular
if hasattr(migration_corridors, '_spectacular') and hasattr(migration_corridors, 'cls'):
    migration_corridors.cls._spectacular = migration_corridors._spectacular
if hasattr(migration_by_sector, '_spectacular') and hasattr(migration_by_sector, 'cls'):
    migration_by_sector.cls._spectacular = migration_by_sector._spectacular
if hasattr(free_movement_stats, '_spectacular') and hasattr(free_movement_stats, 'cls'):
    free_movement_stats.cls._spectacular = free_movement_stats._spectacular
if hasattr(intra_regional_trade, '_spectacular') and hasattr(intra_regional_trade, 'cls'):
    intra_regional_trade.cls._spectacular = intra_regional_trade._spectacular
