"""Monitoring middleware and health endpoints.

Per Architecture Contract §13 (Monitoring & Observability).
Pure-Python fallback — no external prometheus_client dependency.
Production: install prometheus-client for real metrics.
"""

import time
import logging
import json

from django.http import JsonResponse, HttpResponse

logger = logging.getLogger("abia.metrics")

# In-memory metrics storage (resets on restart — dev only)
_request_counts = {}
_request_latencies = []
_db_query_counts = {}
_db_query_latencies = []
_active_requests = 0


class PrometheusMetricsMiddleware:
    """Collect request metrics for monitoring."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _active_requests
        _active_requests += 1
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        _active_requests -= 1

        endpoint = request.resolver_match.route if request.resolver_match else "unknown"
        status = str(response.status_code)
        key = f"{request.method}:{endpoint}:{status}"

        _request_counts[key] = _request_counts.get(key, 0) + 1
        _request_latencies.append(duration)

        # Log slow requests (> 500ms threshold per §13)
        if duration > 0.5:
            logger.warning(
                "Slow request: %s %s took %.3fs (status %s)",
                request.method, request.path, duration, status
            )

        return response


def health_check(request):
    """Health endpoint for container orchestration.

    Returns 200 if Django and DB are reachable.
    Returns 503 if DB is down.
    """
    from django.db import connections
    from django.db.utils import OperationalError

    checks = {
        "django": True,
        "database": False,
    }

    try:
        connections["default"].cursor()
        checks["database"] = True
    except OperationalError:
        logger.error("Health check failed: database unreachable")
        return JsonResponse(
            {"status": "unhealthy", "checks": checks},
            status=503,
        )

    return JsonResponse(
        {"status": "healthy", "checks": checks},
        status=200,
    )


def metrics_endpoint(request):
    """Prometheus-compatible metrics scrape endpoint.

    Pure-Python fallback. Returns text in Prometheus exposition format.
    """
    lines = ["# HELP django_http_requests_total Total HTTP requests\n"]
    lines.append("# TYPE django_http_requests_total counter\n")
    for key, count in _request_counts.items():
        method, endpoint, status = key.split(":")
        lines.append(
            f'django_http_requests_total{{method="{method}",endpoint="{endpoint}",status_code="{status}"}} {count}\n'
        )

    lines.append("\n# HELP django_http_request_duration_seconds HTTP request latency\n")
    lines.append("# TYPE django_http_request_duration_seconds histogram\n")
    if _request_latencies:
        for bucket in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, float("inf")]:
            count = sum(1 for lat in _request_latencies if lat <= bucket)
            lines.append(
                f'django_http_request_duration_seconds_bucket{{le="{bucket}"}} {count}\n'
            )
        lines.append(
            f'django_http_request_duration_seconds_sum {sum(_request_latencies)}\n'
        )
        lines.append(
            f'django_http_request_duration_seconds_count {len(_request_latencies)}\n'
        )

    lines.append("\n# HELP django_http_active_requests Number of active HTTP requests\n")
    lines.append("# TYPE django_http_active_requests gauge\n")
    lines.append(f"django_http_active_requests {_active_requests}\n")

    return HttpResponse("".join(lines), content_type="text/plain; version=0.0.4; charset=utf-8")


class APIVersionMiddleware:
    """Add API version headers to all responses."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            response['X-API-Version'] = 'v1'
            response['X-API-Deprecated'] = 'false'
            response['X-API-Sunset'] = ''
        return response


class PrometheusMiddleware:
    """Track request metrics for Prometheus."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        from .metrics import REQUEST_COUNT, REQUEST_LATENCY

        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        endpoint = request.resolver_match.url_name if request.resolver_match else 'unknown'
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()

        return response
