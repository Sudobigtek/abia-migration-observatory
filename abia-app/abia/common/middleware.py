class APIVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-API-Version"] = "1.0.0"
        return response


class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok", "service": "abia-migration-observatory"})

def metrics_endpoint(request):
    return JsonResponse({"metrics": {"requests_total": 0, "errors_total": 0}})
