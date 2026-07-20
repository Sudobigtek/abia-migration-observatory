class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            request.tenant_lga = getattr(user, "lga", None)
            request.tenant_role = getattr(user, "role", None)
        else:
            request.tenant_lga = None
            request.tenant_role = None
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        return None