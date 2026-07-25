from drf_spectacular.utils import extend_schema
from abia.common.response_serializers import (
    GatewayKeyRotateResponse,
    GatewayRoutesResponse,
    GatewayStatusResponse,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import json

@extend_schema(responses=GatewayStatusResponse, tags=["System"], summary="Gateway health status")
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

@extend_schema(responses=GatewayRoutesResponse, tags=["System"], summary="List gateway routes")
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

@extend_schema(responses=GatewayKeyRotateResponse, tags=["System"], summary="Rotate gateway API key")
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



gateway_key_rotate.cls.serializer_class = GatewayKeyRotateResponse
# Propagate _spectacular metadata for drf-spectacular
if hasattr(gateway_status, '_spectacular') and hasattr(gateway_status, 'cls'):
    gateway_status.cls._spectacular = gateway_status._spectacular
if hasattr(gateway_routes, '_spectacular') and hasattr(gateway_routes, 'cls'):
    gateway_routes.cls._spectacular = gateway_routes._spectacular
if hasattr(gateway_key_rotate, '_spectacular') and hasattr(gateway_key_rotate, 'cls'):
    gateway_key_rotate.cls._spectacular = gateway_key_rotate._spectacular
