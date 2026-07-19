from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SMSCampaign, SMSLog
from .tasks import execute_sms_campaign, send_individual_sms

class SMSCampaignViewSet(viewsets.ModelViewSet):
    queryset = SMSCampaign.objects.prefetch_related("target_lgas")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import SMSCampaignSerializer
        return SMSCampaignSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != "draft":
            return Response({"error": "Campaign already processed"}, status=400)
        campaign.status = "scheduled"
        campaign.save(update_fields=["status"])
        execute_sms_campaign.delay(str(campaign.id))
        return Response({
            "status": "scheduled",
            "campaign_id": str(campaign.id),
            "message": "Campaign queued for delivery"
        })

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        campaign = self.get_object()
        return Response({
            "total": campaign.total_recipients,
            "sent": campaign.sent_count,
            "failed": campaign.failed_count,
            "pending": campaign.total_recipients - campaign.sent_count - campaign.failed_count,
            "status": campaign.status
        })

class SMSLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SMSLog.objects.select_related("campaign", "recipient")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import SMSLogSerializer
        return SMSLogSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_single_sms(request):
    migrant_id = request.data.get("migrant_id")
    message = request.data.get("message")
    if not migrant_id or not message:
        return Response({"error": "migrant_id and message required"}, status=400)
    result = send_individual_sms.delay(migrant_id, message)
    return Response({
        "status": "queued",
        "task_id": result.id,
        "message": "SMS queued for delivery"
    })
