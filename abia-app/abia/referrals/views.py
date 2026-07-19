"""
ABIA Migration Observatory — Referrals API Views
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from abia.referrals.models import Referral
from abia.referrals.serializers import (
    ReferralListSerializer, ReferralDetailSerializer, ReferralCreateUpdateSerializer,
)


class ReferralPermission(IsAuthenticated):
    """Permission hierarchy for referrals."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "super_admin":
            return True
        if user.role == "state_admin":
            return True
        if user.role == "lga_coordinator":
            return obj.from_lga_id == user.lga_id or obj.to_lga_id == user.lga_id
        if user.role == "field_officer":
            return obj.created_by == user or obj.from_lga_id == user.lga_id
        return False


class ReferralViewSet(viewsets.ModelViewSet):
    """
    CRUD + workflow actions for Referral management.

    Endpoints:
    - GET /api/v1/referrals/ — List referrals
    - POST /api/v1/referrals/ — Create referral
    - GET /api/v1/referrals/{id}/ — Referral detail
    - POST /api/v1/referrals/{id}/accept/ — Accept referral
    - POST /api/v1/referrals/{id}/reject/ — Reject referral
    - POST /api/v1/referrals/{id}/complete/ — Complete referral
    - GET /api/v1/referrals/stats/ — Aggregate statistics
    """
    permission_classes = [ReferralPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "from_lga", "to_lga", "case"]
    search_fields = ["reason", "to_organization", "to_contact_name"]
    ordering_fields = ["created_at", "updated_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        base_qs = Referral.objects.select_related(
            "case", "case__migrant", "from_lga", "to_lga", "created_by"
        )

        if user.role in ["super_admin", "state_admin"]:
            return base_qs
        if user.role == "lga_coordinator":
            return base_qs.filter(
                Q(from_lga_id=user.lga_id) | Q(to_lga_id=user.lga_id)
            )
        if user.role == "field_officer":
            return base_qs.filter(
                Q(created_by=user) | Q(from_lga_id=user.lga_id)
            )
        return base_qs.none()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ReferralCreateUpdateSerializer
        if self.action == "retrieve":
            return ReferralDetailSerializer
        return ReferralListSerializer

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Accept a pending referral."""
        referral = self.get_object()
        if referral.status != "pending":
            return Response({"error": "Only pending referrals can be accepted"}, status=status.HTTP_400_BAD_REQUEST)
        referral.status = "accepted"
        referral.save(update_fields=["status", "updated_at"])
        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a referral with reason."""
        referral = self.get_object()
        if referral.status != "pending":
            return Response({"error": "Only pending referrals can be rejected"}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get("rejection_reason", "")
        referral.status = "rejected"
        referral.save(update_fields=["status", "updated_at"])
        return Response({"status": "rejected", "reason": reason})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark referral as completed."""
        referral = self.get_object()
        if referral.status not in ["pending", "accepted"]:
            return Response({"error": "Only pending or accepted referrals can be completed"}, status=status.HTTP_400_BAD_REQUEST)
        referral.status = "completed"
        referral.save(update_fields=["status", "updated_at"])
        return Response({"status": "completed"})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Aggregate referral statistics."""
        qs = self.get_queryset()
        total = qs.count()
        by_status = dict(qs.values("status").annotate(count=Count("id")).values_list("status", "count"))
        by_from_lga = dict(qs.values("from_lga__name").annotate(count=Count("id")).values_list("from_lga__name", "count"))
        by_to_lga = dict(qs.values("to_lga__name").annotate(count=Count("id")).values_list("to_lga__name", "count"))

        return Response({
            "total_referrals": total,
            "by_status": by_status,
            "by_from_lga": by_from_lga,
            "by_to_lga": by_to_lga,
            "pending": qs.filter(status="pending").count(),
            "overdue": qs.filter(status="pending", created_at__lt=__import__('django.utils.timezone').utils.timezone.now() - __import__('datetime').timedelta(days=7)).count(),
        })

    @action(detail=False, methods=["get"])
    def pending_by_lga(self, request):
        """Get pending referrals grouped by destination LGA."""
        from django.db.models import Count
        data = self.get_queryset().filter(status="pending").values(
            "to_lga__name", "to_lga__id"
        ).annotate(count=Count("id")).order_by("-count")
        return Response(list(data))
