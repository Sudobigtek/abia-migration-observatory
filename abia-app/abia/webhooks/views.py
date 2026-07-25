from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    RetryFailedResponse,
    TriggerEventResponse,
    WebhookStatsResponse,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import WebhookEndpoint, WebhookDelivery
from .services import WebhookService
from .serializers import WebhookEndpointSerializer, WebhookDeliverySerializer

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebhookDelivery.objects.select_related("webhook")
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated]

@extend_schema(responses=TriggerEventResponse, tags=["Webhooks"], summary="Trigger webhook event manually")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_event(request):
    event_type = request.data.get("event_type")
    payload = request.data.get("payload", {})
    if not event_type:
        return Response({"error": "event_type required"}, status=400)
    results = WebhookService.trigger_event(event_type, payload)
    return Response({"status": "triggered", "deliveries": results})


trigger_event.cls.serializer_class = TriggerEventResponse
@extend_schema(responses=RetryFailedResponse, tags=["Webhooks"], summary="Retry failed webhook deliveries")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def retry_failed(request):
    webhook_id = request.data.get("webhook_id")
    retried = WebhookService.retry_failed(webhook_id)
    return Response({"status": "retry_completed", "retried_count": retried})


retry_failed.cls.serializer_class = RetryFailedResponse
@extend_schema(responses=WebhookStatsResponse, tags=["Webhooks"], summary="Webhook delivery statistics")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def webhook_stats(request):
    from django.db.models import Count
    stats = {
        "total_endpoints": WebhookEndpoint.objects.filter(is_active=True).count(),
        "total_deliveries": WebhookDelivery.objects.count(),
        "delivered": WebhookDelivery.objects.filter(status="delivered").count(),
        "failed": WebhookDelivery.objects.filter(status="failed").count(),
        "pending": WebhookDelivery.objects.filter(status="pending").count(),
        "by_event": list(WebhookDelivery.objects.values("event_type").annotate(count=Count("id")).order_by("-count")[:10]),
    }
    return Response(stats)


# Propagate _spectacular metadata for drf-spectacular
if hasattr(trigger_event, '_spectacular') and hasattr(trigger_event, 'cls'):
    trigger_event.cls._spectacular = trigger_event._spectacular
if hasattr(retry_failed, '_spectacular') and hasattr(retry_failed, 'cls'):
    retry_failed.cls._spectacular = retry_failed._spectacular
if hasattr(webhook_stats, '_spectacular') and hasattr(webhook_stats, 'cls'):
    webhook_stats.cls._spectacular = webhook_stats._spectacular
