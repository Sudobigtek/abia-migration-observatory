from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonBurstRateThrottle(AnonRateThrottle):
    rate = "10/minute"
    scope = "anon_burst"

class AnonSustainedRateThrottle(AnonRateThrottle):
    rate = "100/day"
    scope = "anon_sustained"

class UserBurstRateThrottle(UserRateThrottle):
    rate = "60/minute"
    scope = "user_burst"

class UserSustainedRateThrottle(UserRateThrottle):
    rate = "1000/day"
    scope = "user_sustained"

class AdminRateThrottle(UserRateThrottle):
    rate = "10000/day"
    scope = "admin"

    def allow_request(self, request, view):
        if hasattr(request.user, "tenant_role") and request.user.tenant_role.role in ["state_admin", "super_admin"]:
            return True
        return super().allow_request(request, view)

class LGARateThrottle(UserRateThrottle):
    rate = "500/day"
    scope = "lga"

    def get_cache_key(self, request, view):
        if hasattr(request.user, "tenant_role") and request.user.tenant_role.lga:
            ident = f"lga_{request.user.tenant_role.lga_id}"
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }