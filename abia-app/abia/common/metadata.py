from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


@extend_schema(
    responses=inline_serializer("MetadataResponse", fields={
        "service": serializers.CharField(),
        "version": serializers.CharField(),
        "status": serializers.CharField(),
        "database": serializers.CharField(),
        "environment": serializers.CharField(),
        "schema_url": serializers.CharField(),
        "docs_url": serializers.CharField(),
        "timestamp": serializers.DateTimeField(),
        "jurisdiction": serializers.DictField(),
        "capabilities": serializers.ListField(child=serializers.CharField()),
    }),
    tags=["System"],
    summary="API metadata and health",
    description="Returns discovery metadata for replication, monitoring, and interoperability with other state systems.",
)
@api_view(["GET"])
def api_metadata(request):
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    return Response({
        "service": "Abia Migration Observatory API",
        "version": settings.SPECTACULAR_SETTINGS.get("VERSION", "1.0.0"),
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "environment": getattr(settings, "ENVIRONMENT", "production"),
        "schema_url": "/api/schema/",
        "docs_url": "/api/docs/",
        "timestamp": timezone.now().isoformat(),
        "jurisdiction": {
            "country": "Nigeria",
            "state": "Abia",
            "level": "subnational",
        },
        "capabilities": [
            "migrant-registry",
            "case-management",
            "risk-assessment",
            "referral-tracking",
            "document-storage",
            "analytics",
            "dynamic-fields",
            "report-generation",
        ],
    })


@extend_schema(
    responses=inline_serializer("HealthResponse", fields={
        "status": serializers.CharField(),
    }),
    tags=["System"],
    summary="Health check",
    description="Simple health check for load balancers, Docker, and uptime monitoring.",
)
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})
