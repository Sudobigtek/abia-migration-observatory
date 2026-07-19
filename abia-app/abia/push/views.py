from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PushDevice, PushNotification
from .serializers import PushDeviceSerializer, PushNotificationSerializer

class PushDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = PushDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PushDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register or update a device token."""
        token = request.data.get('device_token')
        platform = request.data.get('platform', 'android')
        device_name = request.data.get('device_name', '')
        
        if not token:
            return Response({'error': 'device_token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        device, created = PushDevice.objects.update_or_create(
            device_token=token,
            defaults={
                'user': request.user,
                'platform': platform,
                'device_name': device_name,
                'is_active': True
            }
        )
        return Response({
            'status': 'registered' if created else 'updated',
            'device_id': str(device.id)
        })

    @action(detail=False, methods=['post'])
    def unregister(self, request):
        """Deactivate a device token."""
        token = request.data.get('device_token')
        if not token:
            return Response({'error': 'device_token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        PushDevice.objects.filter(device_token=token, user=request.user).update(is_active=False)
        return Response({'status': 'unregistered'})

class PushNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PushNotification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(status='pending').update(status='delivered')
        return Response({'status': 'all_marked_delivered'})
