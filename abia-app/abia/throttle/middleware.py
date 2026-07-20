from django.utils import timezone
from datetime import timedelta
from .models import RateLimitLog

class RateLimitLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 429:
            ip = self.get_client_ip(request)
            RateLimitLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=ip,
                endpoint=request.path,
                method=request.method,
                was_throttled=True,
                window_start=timezone.now()
            )
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")