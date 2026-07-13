"""Shared filtering utilities."""
class LGAFilterMixin:
    def filter_queryset_by_lga(self, queryset, request):
        user = request.user
        if getattr(user, "role", None) in ("state_admin", "super_admin"):
            return queryset
        lga = getattr(user, "lga", None)
        if lga:
            return queryset.filter(current_lga=lga) if hasattr(queryset.model, "current_lga") else queryset.filter(lga=lga)
        return queryset.none()
