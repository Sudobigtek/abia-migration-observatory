from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def api_version(min_version='v1', max_version='v1', deprecated_in=None, sunset_date=None):
    """Decorator to mark API endpoint version compatibility."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            requested_version = request.headers.get('X-API-Version', 'v1')
            if requested_version < min_version or requested_version > max_version:
                return Response(
                    {'error': f'API version {requested_version} not supported. Use {min_version}-{max_version}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            response = func(request, *args, **kwargs)
            if isinstance(response, Response):
                if deprecated_in:
                    response['X-API-Deprecated'] = 'true'
                    response['X-API-Deprecation-Notice'] = f'Deprecated in {deprecated_in}'
                if sunset_date:
                    response['X-API-Sunset'] = str(sunset_date)
            return response
        return wrapper
    return decorator
