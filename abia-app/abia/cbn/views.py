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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_summary(request):
    return Response(CBNService.get_summary())

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_by_lga(request):
    return Response({"lgas": CBNService.get_by_lga()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_by_channel(request):
    return Response({"channels": CBNService.get_by_channel()})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def remittance_trends(request):
    return Response({"trends": CBNService.get_monthly_trends()})