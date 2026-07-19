import logging
import time

logger = logging.getLogger("abia.api")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = (time.time() - start) * 1000

        logger.info(
            "%s %s %s %s %.2fms %s",
            request.method,
            request.path,
            response.status_code,
            request.user.username if request.user.is_authenticated else "anon",
            duration,
            request.META.get("REMOTE_ADDR", "unknown"),
        )
        return response
