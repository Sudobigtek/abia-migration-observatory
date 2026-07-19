from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import json

@api_view(['GET'])
@permission_classes([AllowAny])
def gateway_status(request):
    """Return API gateway status and routing info."""
    return Response({
        'gateway': 'kong',
        'status': 'active',
        'version': '3.x',
        'routes': {
            'api_v1': '/api/v1/',
            'health': '/health/',
            'metrics': '/metrics/',
            'docs': '/api/v1/docs/',
        },
        'features': {
            'rate_limiting': True,
            'authentication': True,
            'cors': True,
            'logging': True,
        },
        'environment': settings.DEBUG and 'development' or 'production',
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gateway_routes(request):
    """Return available API routes for the gateway."""
    from django.urls import get_resolver
    
    resolver = get_resolver()
    routes = []
    
    for url_pattern in resolver.url_patterns:
        if hasattr(url_pattern, 'url_patterns'):
            for sub in url_pattern.url_patterns:
                if hasattr(sub, 'pattern') and hasattr(sub.pattern, 'describe'):
                    routes.append({
                        'path': str(sub.pattern),
                        'name': sub.name or 'unnamed',
                    })
    
    return Response({
        'total_routes': len(routes),
        'routes': routes[:50]  # Limit output
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gateway_key_rotate(request):
    """Rotate API key (placeholder for Kong key-auth integration)."""
    from django.contrib.auth.models import Token
    # In production, this would call Kong Admin API
    return Response({
        'status': 'key_rotation_not_implemented',
        'message': 'Integrate with Kong Admin API for production use',
        'documentation': 'https://docs.konghq.com/gateway/latest/admin-api/#key-auth'
    })
