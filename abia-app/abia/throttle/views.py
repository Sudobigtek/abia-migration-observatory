from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from .models import RateLimitLog

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def throttle_stats(request):
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    stats = {
        "total_requests_today": RateLimitLog.objects.filter(created_at__date=today).count(),
        "throttled_requests_today": RateLimitLog.objects.filter(created_at__date=today, was_throttled=True).count(),
        "top_endpoints": list(RateLimitLog.objects.filter(created_at__date=today).values("endpoint").annotate(count=Count("id")).order_by("-count")[:10]),
        "top_ips": list(RateLimitLog.objects.filter(created_at__date=today).values("ip_address").annotate(count=Count("id")).order_by("-count")[:10]),
        "throttle_limits": {
            "anon_burst": "10/minute",
            "anon_sustained": "100/day",
            "user_burst": "60/minute",
            "user_sustained": "1000/day",
            "admin": "unlimited",
            "lga": "500/day",
        }
    }
    return Response(stats)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_rate_limit(request):
    return Response({
        "user": str(request.user),
        "role": getattr(request.user, "tenant_role", None) and request.user.tenant_role.role or None,
        "limits": {
            "burst": "60/minute",
            "sustained": "1000/day",
        }
        if request.user.is_authenticated else {
            "burst": "10/minute",
            "sustained": "100/day",
        }
    })