from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    RemittanceByChannelResponse,
    RemittanceByLgaResponse,
    RemittanceSummaryResponse,
    RemittanceTrendsResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import RemittanceRecord, CBNConfiguration
from .services import CBNService
from .serializers import RemittanceRecordSerializer, CBNConfigurationSerializer

class RemittanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = RemittanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return RemittanceRecord.objects.all()
        if hasattr(user, "lga") and user.lga:
            return RemittanceRecord.objects.filter(recipient_lga=user.lga)
        return RemittanceRecord.objects.none()

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class CBNConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = CBNConfigurationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = CBNConfiguration.objects.all()

@extend_schema(responses=RemittanceSummaryResponse, tags=["CBN"], summary="Remittance summary")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_summary(request):
    return Response(CBNService.get_summary())

@extend_schema(responses=RemittanceByLgaResponse, tags=["CBN"], summary="Remittances by LGA")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_by_lga(request):
    return Response({"lgas": CBNService.get_by_lga()})

@extend_schema(responses=RemittanceByChannelResponse, tags=["CBN"], summary="Remittances by channel")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_by_channel(request):
    return Response({"channels": CBNService.get_by_channel()})

@extend_schema(responses=RemittanceTrendsResponse, tags=["CBN"], summary="Remittance trends over time")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_trends(request):
    return Response({"trends": CBNService.get_monthly_trends()})


# Propagate _spectacular metadata for drf-spectacular
if hasattr(remittance_summary, '_spectacular') and hasattr(remittance_summary, 'cls'):
    remittance_summary.cls._spectacular = remittance_summary._spectacular
if hasattr(remittance_by_lga, '_spectacular') and hasattr(remittance_by_lga, 'cls'):
    remittance_by_lga.cls._spectacular = remittance_by_lga._spectacular
if hasattr(remittance_by_channel, '_spectacular') and hasattr(remittance_by_channel, 'cls'):
    remittance_by_channel.cls._spectacular = remittance_by_channel._spectacular
if hasattr(remittance_trends, '_spectacular') and hasattr(remittance_trends, 'cls'):
    remittance_trends.cls._spectacular = remittance_trends._spectacular
