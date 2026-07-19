from rest_framework import permissions
from .permissions import LGAScopedPermission

class LGAScopedViewSetMixin:
    """Mixin to automatically filter queryset by user's LGA."""
    permission_classes = [permissions.IsAuthenticated, LGAScopedPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role in ['super_admin', 'state_admin']:
            return queryset
        user_lga = getattr(user, 'lga', None)
        if user_lga:
            # Try common LGA field names
            if hasattr(queryset.model, 'current_lga'):
                return queryset.filter(current_lga=user_lga)
            elif hasattr(queryset.model, 'lga'):
                return queryset.filter(lga=user_lga)
        return queryset
