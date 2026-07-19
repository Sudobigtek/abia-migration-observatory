from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonBurstRateThrottle(AnonRateThrottle):
    """Strict rate limit for anonymous users."""
    rate = '10/minute'
    scope = 'anon_burst'

class AnonSustainedRateThrottle(AnonRateThrottle):
    """Daily limit for anonymous users."""
    rate = '100/day'
    scope = 'anon_sustained'

class UserBurstRateThrottle(UserRateThrottle):
    """Per-minute limit for authenticated users."""
    rate = '60/minute'
    scope = 'user_burst'

class UserSustainedRateThrottle(UserRateThrottle):
    """Daily limit for authenticated users."""
    rate = '5000/day'
    scope = 'user_sustained'

class AdminRateThrottle(UserRateThrottle):
    """Higher limit for admin users."""
    rate = '1000/minute'
    scope = 'admin'

class SearchRateThrottle(UserRateThrottle):
    """Specific limit for search endpoints (expensive)."""
    rate = '30/minute'
    scope = 'search'

class ExportRateThrottle(UserRateThrottle):
    """Specific limit for export endpoints (IO-heavy)."""
    rate = '10/minute'
    scope = 'export'
