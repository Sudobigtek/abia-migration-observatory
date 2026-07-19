"""
ABIA Migration Observatory — Accounts API Views
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from abia.accounts.models import LGA
from abia.accounts.serializers import LGASerializer, UserListSerializer, UserDetailSerializer

User = get_user_model()


class LGAPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class LGAViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only LGA data for dropdowns and maps."""
    queryset = LGA.objects.prefetch_related("users", "cases", "migrants")
    serializer_class = LGASerializer
    permission_classes = [LGAPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["code"]
    search_fields = ["name", "code"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Get statistics for a specific LGA."""
        lga = self.get_object()
        return Response({
            "lga": lga.name,
            "users": lga.users.count(),
            "cases": lga.cases.count(),
            "migrants": lga.migrants.count(),
            "referrals_sent": lga.referrals_sent.count(),
            "referrals_received": lga.referrals_received.count(),
        })


class UserPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "super_admin":
            return True
        if user.role == "state_admin":
            return True
        if user.role == "lga_coordinator":
            return obj.lga_id == user.lga_id
        return obj == user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only user data (for assignment dropdowns, etc.)."""
    serializer_class = UserListSerializer
    permission_classes = [UserPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role", "lga", "is_active"]
    search_fields = ["first_name", "last_name", "username", "email"]
    ordering = ["first_name"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["super_admin", "state_admin"]:
            return User.objects.select_related("lga")
        if user.role == "lga_coordinator":
            return User.objects.select_related("lga").filter(lga_id=user.lga_id)
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    @action(detail=False, methods=["get"])
    def officers(self, request):
        """Get field officers for case assignment."""
        officers = self.get_queryset().filter(role="field_officer", is_active=True)
        serializer = UserListSerializer(officers, many=True)
        return Response(serializer.data)
