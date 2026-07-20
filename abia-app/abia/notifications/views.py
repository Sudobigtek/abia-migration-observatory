from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification, NotificationPreference
from .services import NotificationService
from .serializers import NotificationSerializer, NotificationPreferenceSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("recipient")

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_read(request, notification_id):
    notif = NotificationService.mark_read(notification_id, request.user)
    return Response({"status": "marked_read", "id": str(notif.id)})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unread_count(request):
    count = NotificationService.get_unread_count(request.user)
    return Response({"unread_count": count})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def broadcast(request):
    role = request.data.get("role")
    title = request.data.get("title")
    message = request.data.get("message")
    priority = request.data.get("priority", "medium")
    if not all([role, title, message]):
        return Response({"error": "role, title, message required"}, status=400)
    sent = NotificationService.broadcast_to_role(role, title, message, priority)
    return Response({"status": "broadcasted", "sent": sent})