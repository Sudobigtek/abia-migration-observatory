from rest_framework import permissions


class LGAAccessPermission(permissions.BasePermission):
    """Ensures users can only access data within their assigned LGA."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) in ("state_admin", "super_admin"):
            return True
        user_lga = getattr(user, "lga", None)
        if user_lga is None:
            return False
        obj_lga = getattr(obj, "lga", None) or getattr(obj, "current_lga", None)
        if obj_lga is None:
            return user.role in ("state_admin", "super_admin")
        return obj_lga == user_lga or obj_lga.id == user_lga.id


class IsStateAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) in ("state_admin", "super_admin")


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) == "super_admin"


class IsFieldOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and getattr(user, "role", None) in ("field_officer", "lga_coordinator", "state_admin", "super_admin")
