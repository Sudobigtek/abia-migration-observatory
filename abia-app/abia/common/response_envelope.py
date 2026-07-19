import json
from django.utils.deprecation import MiddlewareMixin


class EnvelopedResponseMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Skip if already enveloped, or if non-JSON, or if error status
        if response.status_code >= 400:
            return response
        if getattr(response, "_skip_envelope", False):
            return response
        content_type = response.get("Content-Type", "")
        if "application/json" not in content_type:
            return response
        # Skip schema/docs and monitoring endpoints
        if request.path.startswith("/api/schema/") or request.path.startswith("/api/docs/") or request.path.startswith("/health/") or request.path.startswith("/metrics/"):
            return response

        try:
            data = json.loads(response.content)
        except (json.JSONDecodeError, AttributeError):
            return response

        # Skip if already enveloped
        if isinstance(data, dict) and "status" in data and "data" in data:
            return response

        # Paginated responses already have meta — wrap them
        if isinstance(data, dict) and "results" in data:
            enveloped = {
                "status": "success",
                "data": data["results"],
                "meta": {
                    "page": data.get("page", 1),
                    "page_size": len(data["results"]),
                    "total_count": data.get("count", 0),
                    "total_pages": data.get("total_pages", 1),
                },
            }
        else:
            enveloped = {
                "status": "success",
                "data": data,
                "meta": {},
            }

        response.content = json.dumps(enveloped).encode("utf-8")
        response["Content-Length"] = str(len(response.content))
        return response
