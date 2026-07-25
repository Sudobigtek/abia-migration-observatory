from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    AthletesBySportResponse,
    TalentExportResponse,
    TalentMapResponse,
    TopAthletesResponse,
    TransferDestinationResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import AthleteProfile, AthleteTransfer, SportsConfiguration
from .services import SportsService
from .serializers import AthleteProfileSerializer, AthleteTransferSerializer, SportsConfigurationSerializer

class AthleteProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AthleteProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = AthleteProfile.objects.filter(is_active=True)

class AthleteTransferViewSet(viewsets.ModelViewSet):
    serializer_class = AthleteTransferSerializer
    permission_classes = [IsAuthenticated]
    queryset = AthleteTransfer.objects.all()

class SportsConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = SportsConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = SportsConfiguration.objects.all()

@extend_schema(responses=TransferDestinationResponse, tags=["Sports"], summary="Transfers by destination")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transfers_by_destination(request):
    return Response({"destinations": SportsService.get_transfers_by_destination()})

@extend_schema(responses=TalentExportResponse, tags=["Sports"], summary="Talent export value")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def talent_export_value(request):
    return Response(SportsService.get_talent_export_value())

@extend_schema(responses=AthletesBySportResponse, tags=["Sports"], summary="Athletes by sport")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def athletes_by_sport(request):
    return Response({"sports": SportsService.get_by_sport()})

@extend_schema(responses=TopAthletesResponse, tags=["Sports"], summary="Top valued athletes")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_valued_athletes(request):
    limit = int(request.query_params.get("limit", 20))
    return Response({"athletes": SportsService.get_top_valued_athletes(limit)})

@extend_schema(responses=TalentMapResponse, tags=["Sports"], summary="LGA talent map")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lga_talent_map(request):
    return Response({"lgas": SportsService.get_lga_talent_map()})


# Propagate _spectacular metadata for drf-spectacular
if hasattr(transfers_by_destination, '_spectacular') and hasattr(transfers_by_destination, 'cls'):
    transfers_by_destination.cls._spectacular = transfers_by_destination._spectacular
if hasattr(talent_export_value, '_spectacular') and hasattr(talent_export_value, 'cls'):
    talent_export_value.cls._spectacular = talent_export_value._spectacular
if hasattr(athletes_by_sport, '_spectacular') and hasattr(athletes_by_sport, 'cls'):
    athletes_by_sport.cls._spectacular = athletes_by_sport._spectacular
if hasattr(top_valued_athletes, '_spectacular') and hasattr(top_valued_athletes, 'cls'):
    top_valued_athletes.cls._spectacular = top_valued_athletes._spectacular
if hasattr(lga_talent_map, '_spectacular') and hasattr(lga_talent_map, 'cls'):
    lga_talent_map.cls._spectacular = lga_talent_map._spectacular
