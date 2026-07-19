from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import django
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cache_stats_view(request):
    """Return cache statistics."""
    from .cache import cache_stats
    return Response(cache_stats())