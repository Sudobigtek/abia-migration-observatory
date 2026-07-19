from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import WebhookEndpoint, WebhookDelivery
from .serializers import WebhookEndpointSerializer, WebhookDeliverySerializer

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.select_related('created_by')
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'state_admin']:
            return self.queryset
        return self.queryset.filter(created_by=user)

class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebhookDelivery.objects.select_related('endpoint')
    serializer_class = WebhookDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'event_type', 'endpoint']
