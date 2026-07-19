from .services import log_action

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if hasattr(request, "audit_entity"):
                log_action(
                    user=request.user,
                    action=request.audit_action or request.method.lower(),
                    entity_type=request.audit_entity.get("type", "unknown"),
                    entity_id=request.audit_entity.get("id"),
                    entity_repr=request.audit_entity.get("repr", ""),
                    request=request
                )
        return response