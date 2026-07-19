from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'

class IsStateAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'state_admin']

class IsLGACoordinator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'state_admin', 'lga_coordinator']

class IsFieldOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'state_admin', 'lga_coordinator', 'field_officer']

class LGAScopedPermission(permissions.BasePermission):
    """Ensure users can only access data from their assigned LGA (unless super admin)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['super_admin', 'state_admin']:
            return True
        user_lga = getattr(request.user, 'lga', None)
        obj_lga = getattr(obj, 'current_lga', None) or getattr(obj, 'lga', None)
        if user_lga and obj_lga:
            return user_lga == obj_lga
        return True
