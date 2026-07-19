from .models import TenantRole

class TenantService:
    @staticmethod
    def assign_role(user, role, lga=None):
        role_obj, _ = TenantRole.objects.get_or_create(user=user)
        role_obj.role = role
        role_obj.lga = lga
        if role in ["state_admin", "super_admin"]:
            role_obj.can_access_all_lgas = True
        role_obj.save()
        return role_obj

    @staticmethod
    def get_filtered_queryset(user, model_class, lga_field="current_lga"):
        if not hasattr(user, "tenant_role"):
            return model_class.objects.none()
        role = user.tenant_role
        if role.role in ["state_admin", "super_admin"]:
            return model_class.objects.all()
        if role.lga:
            kwargs = {lga_field + "__id": role.lga_id}
            return model_class.objects.filter(**kwargs)
        return model_class.objects.none()