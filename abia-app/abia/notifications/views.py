from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'channel', 'status']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        import django.utils.timezone
        notif.status = 'read'
        notif.read_at = django.utils.timezone.now()
        notif.save()
        return Response({'status': 'marked_read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        import django.utils.timezone
        self.get_queryset().filter(status__in=['pending', 'sent']).update(
            status='read', read_at=django.utils.timezone.now()
        )
        return Response({'status': 'all_marked_read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(status__in=['pending', 'sent']).count()
        return Response({'unread_count': count})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj
