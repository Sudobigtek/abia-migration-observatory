"""
ABIA Migration Observatory — Cases API Views
NASA-level: permissions, spatial filtering, workflow actions, nested resources.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_gis.filters import InBBoxFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone

from abia.cases.models import Case
from abia.cases.serializers import (
    CaseListSerializer, CaseDetailSerializer,
    CaseCreateUpdateSerializer, CaseStatsSerializer,
)


class CasePermission(IsAuthenticated):
    """
    Permission hierarchy:
    - field_officer: can view/create cases in own LGA, edit own cases
    - lga_coordinator: can view all cases in own LGA, assign cases
    - state_admin: can view all cases in state, full CRUD
    - super_admin: full access
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == "super_admin":
            return True
        if user.role == "state_admin":
            return True  # State-level access
        if user.role == "lga_coordinator":
            return obj.lga_id == user.lga_id or obj.created_by.lga_id == user.lga_id
        if user.role == "field_officer":
            return obj.created_by == user or obj.assigned_to == user or obj.lga_id == user.lga_id
        return False

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        if request.method == "POST":
            return request.user.role in ["field_officer", "lga_coordinator", "state_admin", "super_admin"]
        return True


class CaseViewSet(viewsets.ModelViewSet):
    """
    CRUD + workflow actions for Case management.

    Endpoints:
    - GET /api/v1/cases/ — List cases (filtered by permissions)
    - POST /api/v1/cases/ — Create case
    - GET /api/v1/cases/{id}/ — Case detail with referrals
    - PUT /api/v1/cases/{id}/ — Update case
    - POST /api/v1/cases/{id}/assign/ — Assign case to officer
    - POST /api/v1/cases/{id}/resolve/ — Mark case resolved
    - POST /api/v1/cases/{id}/escalate/ — Escalate case
    - GET /api/v1/cases/stats/ — Aggregate statistics
    - GET /api/v1/cases/map_data/ — GeoJSON for map display
    """
    permission_classes = [CasePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InBBoxFilter,
    ]
    filterset_fields = ["status", "priority", "case_type", "lga", "assigned_to"]
    search_fields = ["description", "migrant__full_name", "migrant__phone"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]
    bbox_filter_field = "location"
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        user = self.request.user
        base_qs = Case.objects.select_related(
            "migrant", "assigned_to", "lga", "created_by"
        ).prefetch_related("referrals")

        # Permission-based filtering
        if user.role == "super_admin" or user.role == "state_admin":
            return base_qs
        if user.role == "lga_coordinator":
            return base_qs.filter(
                Q(lga_id=user.lga_id) | Q(created_by__lga_id=user.lga_id)
            )
        if user.role == "field_officer":
            return base_qs.filter(
                Q(created_by=user) | Q(assigned_to=user) | Q(lga_id=user.lga_id)
            )
        return base_qs.none()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CaseCreateUpdateSerializer
        if self.action in ["retrieve"]:
            return CaseDetailSerializer
        return CaseListSerializer

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign case to a specific officer."""
        case = self.get_object()
        officer_id = request.data.get("officer_id")

        if not officer_id:
            return Response({"error": "officer_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        from abia.accounts.models import User
        try:
            officer = User.objects.get(id=officer_id)
        except User.DoesNotExist:
            return Response({"error": "Officer not found"}, status=status.HTTP_404_NOT_FOUND)

        case.assigned_to = officer
        case.status = "in_progress"
        case.save(update_fields=["assigned_to", "status", "updated_at"])

        return Response({
            "status": "assigned",
            "assigned_to": officer.get_full_name(),
            "case_status": case.status,
        })

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark case as resolved."""
        case = self.get_object()
        case.status = "resolved"
        case.resolved_at = timezone.now()
        case.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response({"status": "resolved", "resolved_at": case.resolved_at})

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        """Escalate case priority."""
        case = self.get_object()
        new_priority = request.data.get("priority", "high")
        if new_priority not in ["low", "medium", "high", "critical"]:
            return Response({"error": "Invalid priority"}, status=status.HTTP_400_BAD_REQUEST)

        case.priority = new_priority
        case.status = "escalated"
        case.save(update_fields=["priority", "status", "updated_at"])
        return Response({"status": "escalated", "priority": case.priority})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Aggregate case statistics."""
        qs = self.get_queryset()

        total = qs.count()
        by_status = dict(qs.values("status").annotate(count=Count("id")).values_list("status", "count"))
        by_type = dict(qs.values("case_type").annotate(count=Count("id")).values_list("case_type", "count"))
        by_priority = dict(qs.values("priority").annotate(count=Count("id")).values_list("priority", "count"))
        by_lga = dict(qs.values("lga__name").annotate(count=Count("id")).values_list("lga__name", "count"))

        resolved = qs.filter(resolved_at__isnull=False)
        avg_days = None
        if resolved.exists():
            avg_days = resolved.annotate(
                duration=ExpressionWrapper(
                    F("resolved_at") - F("created_at"), output_field=DurationField()
                )
            ).aggregate(avg=Avg("duration"))["avg"]
            if avg_days:
                avg_days = avg_days.total_seconds() / 86400

        return Response({
            "total_cases": total,
            "by_status": by_status,
            "by_type": by_type,
            "by_priority": by_priority,
            "by_lga": by_lga,
            "avg_resolution_days": round(avg_days, 2) if avg_days else 0,
            "open_cases": qs.filter(status__in=["open", "in_progress"]).count(),
            "critical_cases": qs.filter(priority="critical", status__in=["open", "in_progress", "escalated"]).count(),
        })

    @action(detail=False, methods=["get"])
    def map_data(self, request):
        """Get all cases with location for map display."""
        cases = self.get_queryset().filter(location__isnull=False).only(
            "id", "case_type", "status", "priority", "location"
        )
        serializer = CaseDetailSerializer(cases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_cases(self, request):
        """Get cases assigned to or created by the current user."""
        user = request.user
        cases = self.get_queryset().filter(
            Q(assigned_to=user) | Q(created_by=user)
        )
        page = self.paginate_queryset(cases)
        if page is not None:
            serializer = CaseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CaseListSerializer(cases, many=True)
        return Response(serializer.data)
