from rest_framework import permissions

class LGAAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not hasattr(user, "tenant_role"):
            return False
        role = user.tenant_role
        if role.role in ["state_admin", "super_admin"]:
            return True
        lga_field = getattr(obj, "current_lga", None) or getattr(obj, "lga", None)
        if lga_field:
            return role.can_access_lga(lga_field.id)
        return False

class IsStateAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, "tenant_role") and request.user.tenant_role.role in ["state_admin", "super_admin"]

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, "tenant_role") and request.user.tenant_role.role == "super_admin"