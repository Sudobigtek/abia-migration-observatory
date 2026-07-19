from rest_framework import serializers
from .models import TenantRole

class TenantRoleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    lga_name = serializers.CharField(source="lga.name", read_only=True)
    class Meta:
        model = TenantRole
        fields = ["id", "user", "user_name", "role", "lga", "lga_name",
                  "can_access_all_lgas", "created_at", "updated_at"]