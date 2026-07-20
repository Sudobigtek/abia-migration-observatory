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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transfers_by_destination(request):
    return Response({"destinations": SportsService.get_transfers_by_destination()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def talent_export_value(request):
    return Response(SportsService.get_talent_export_value())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def athletes_by_sport(request):
    return Response({"sports": SportsService.get_by_sport()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_valued_athletes(request):
    limit = int(request.query_params.get("limit", 20))
    return Response({"athletes": SportsService.get_top_valued_athletes(limit)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lga_talent_map(request):
    return Response({"lgas": SportsService.get_lga_talent_map()})