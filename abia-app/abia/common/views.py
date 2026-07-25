from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    ApiVersionInfoResponse,
    CacheStatsResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import django
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

@extend_schema(responses=ApiVersionInfoResponse, tags=["System"], summary="API version information")
@api_view(['GET'])
@permission_classes([AllowAny])
def api_version_info(request):
    """Return API version and system info."""
    from django.conf import settings
    return Response({
        'api_version': 'v1',
        'api_status': 'stable',
        'django_version': django.get_version(),
        'supported_versions': ['v1'],
        'deprecated_versions': [],
        'upcoming_versions': ['v2'],
        'documentation': '/api/v1/docs/',
        'health_check': '/health/',
    })


@extend_schema(responses=CacheStatsResponse, tags=["System"], summary="Cache statistics")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cache_stats_view(request):
    """Return cache statistics."""
    from .cache import cache_stats
    return Response(cache_stats())


# Propagate _spectacular metadata for drf-spectacular
if hasattr(api_version_info, '_spectacular') and hasattr(api_version_info, 'cls'):
    api_version_info.cls._spectacular = api_version_info._spectacular
if hasattr(cache_stats_view, '_spectacular') and hasattr(cache_stats_view, 'cls'):
    cache_stats_view.cls._spectacular = cache_stats_view._spectacular
