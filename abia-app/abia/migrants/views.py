"""
ABIA Migration Observatory — Migrants API Views
NASA-level design: filtering, spatial queries, pagination, permissions.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_gis.filters import InBBoxFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from abia.migrants.models import Migrant, MigrantVersion, PhotoUploadQueue
from abia.migrants.serializers import (
    MigrantListSerializer,
    MigrantDetailSerializer,
    MigrantCreateUpdateSerializer,
    MigrantVersionSerializer,
    PhotoUploadQueueSerializer,
)


class MigrantViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Migrant records.

    Supports:
    - Full text search on name, phone, email
    - Spatial filtering by bounding box
    - Status filtering
    - LGA filtering
    - GeoJSON output for map integration
    """
    queryset = Migrant.objects.select_related(
        "current_lga", "created_by"
    ).prefetch_related("versions", "photo_queue")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InBBoxFilter,
    ]
    filterset_fields = ["status", "gender", "nationality", "current_lga"]
    search_fields = ["full_name", "phone", "email", "id_number", "odk_submission_id"]
    ordering_fields = ["created_at", "updated_at", "full_name", "status"]
    ordering = ["-created_at"]
    bbox_filter_field = "location"
    bbox_filter_include_overlapping = True

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MigrantCreateUpdateSerializer
        if self.action == "retrieve":
            return MigrantDetailSerializer
        return MigrantListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Spatial proximity filter
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")
        radius = self.request.query_params.get("radius", 5000)  # meters

        if lat and lon:
            point = Point(float(lon), float(lat), srid=4326)
            queryset = queryset.filter(location__distance_lte=(point, D(m=radius)))

        # Date range filter
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        """Get audit trail for a migrant."""
        migrant = self.get_object()
        versions = migrant.versions.all()
        serializer = MigrantVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def photos(self, request, pk=None):
        """Get photo upload queue for a migrant."""
        migrant = self.get_object()
        photos = migrant.photo_queue.all()
        serializer = PhotoUploadQueueSerializer(photos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get aggregate statistics."""
        from django.db.models import Count, Q

        total = Migrant.objects.count()
        by_status = dict(Migrant.objects.values("status").annotate(count=Count("id")).values_list("status", "count"))
        by_gender = dict(Migrant.objects.values("gender").annotate(count=Count("id")).values_list("gender", "count"))
        by_nationality = dict(Migrant.objects.values("nationality").annotate(count=Count("id")).values_list("nationality", "count"))
        pending_photos = PhotoUploadQueue.objects.filter(status="pending").count()

        return Response({
            "total_migrants": total,
            "by_status": by_status,
            "by_gender": by_gender,
            "by_nationality": by_nationality,
            "pending_photo_uploads": pending_photos,
        })

    @action(detail=False, methods=["get"])
    def map_data(self, request):
        """Get all migrants with location for map display."""
        migrants = Migrant.objects.filter(location__isnull=False).only(
            "id", "full_name", "status", "location"
        )
        serializer = MigrantDetailSerializer(migrants, many=True)
        return Response(serializer.data)


class MigrantVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only audit trail viewset."""
    queryset = MigrantVersion.objects.select_related("migrant", "edited_by", "current_lga")
    serializer_class = MigrantVersionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["migrant", "edited_by"]
    ordering = ["-created_at"]


class PhotoUploadQueueViewSet(viewsets.ModelViewSet):
    """Photo upload queue management."""
    queryset = PhotoUploadQueue.objects.select_related("migrant")
    serializer_class = PhotoUploadQueueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "migrant"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """Mark a photo for retry."""
        photo = self.get_object()
        if photo.retry_count >= 3:
            photo.status = "failed"
            photo.last_error = "Max retry count exceeded"
        else:
            photo.retry_count += 1
            photo.status = "retrying"
        photo.save()
        return Response({"status": photo.status, "retry_count": photo.retry_count})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a photo as completed."""
        photo = self.get_object()
        photo.status = "completed"
        photo.save()
        return Response({"status": "completed"})
