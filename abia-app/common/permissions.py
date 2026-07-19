from rest_framework import permissions


class LGAAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ["state_admin", "super_admin"]:
            return True
        if hasattr(obj, "lga"):
            return obj.lga_id == user.lga_id
        if hasattr(obj, "current_lga"):
            return obj.current_lga_id == user.lga_id
        if hasattr(obj, "from_lga"):
            return obj.from_lga_id == user.lga_id or obj.to_lga_id == user.lga_id
        return True
