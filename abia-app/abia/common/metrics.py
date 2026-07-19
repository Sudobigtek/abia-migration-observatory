from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

# Define metrics
REQUEST_COUNT = Counter(
    'django_request_count',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'django_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'django_active_users',
    'Number of active users'
)

DB_QUERY_COUNT = Counter(
    'django_db_query_count',
    'Total database queries',
    ['model']
)

def metrics_endpoint(request):
    """Prometheus metrics endpoint."""
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
