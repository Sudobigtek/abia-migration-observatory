from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json

def cache_key(prefix, *args, **kwargs):
    """Generate a deterministic cache key."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    hash_suffix = hashlib.md5(key_data.encode()).hexdigest()[:12]
    return f"abia:{prefix}:{hash_suffix}"

def cached_view(timeout=300, key_prefix='view'):
    """Decorator to cache DRF view responses."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return func(request, *args, **kwargs)
            
            # Build cache key from request
            cache_k = cache_key(
                key_prefix,
                request.path,
                dict(request.query_params),
                str(request.user.id) if request.user.is_authenticated else 'anon'
            )
            
            cached = cache.get(cache_k)
            if cached is not None:
                return cached
            
            response = func(request, *args, **kwargs)
            
            # Cache only successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                cache.set(cache_k, response, timeout=timeout)
            
            return response
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern."""
    # Django's cache backend doesn't support pattern deletion natively
    # For Redis, we'd use redis-cli directly
    from django_redis import get_redis_connection
    try:
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"abia:{pattern}:*")
        if keys:
            redis_conn.delete(*keys)
            return {'deleted': len(keys)}
    except Exception:
        pass
    return {'deleted': 0}

def cache_stats():
    """Return cache statistics."""
    from django_redis import get_redis_connection
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        return {
            'used_memory_human': info.get('used_memory_human', 'unknown'),
            'connected_clients': info.get('connected_clients', 0),
            'total_keys': redis_conn.dbsize(),
            'hit_rate': info.get('keyspace_hits', 0) / max(
                info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1
            ),
        }
    except Exception as e:
        return {'error': str(e)}
