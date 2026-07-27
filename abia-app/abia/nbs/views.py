"""Admin-only NBS export preparation endpoints."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


@extend_schema(
    responses=inline_serializer("NBSExportStatus", fields={
        "status": serializers.CharField(),
        "available_formats": serializers.ListField(
            child=serializers.CharField()
        ),
    }),
    tags=["NBS Connector"],
    summary="Prepare NBS export",
    description="Admin-only endpoint to validate and package data for NBS submission.",
)
@api_view(["GET"])
@permission_classes([IsAdminUser])
def prepare_nbs_export(request):
    """Return available export formats for NBS submission."""
    return Response({
        "status": "ready",
        "available_formats": ["xlsx", "xml", "json"],
    })
