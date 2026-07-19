from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TenantRole
from .permissions import LGAAccessPermission
from .serializers import TenantRoleSerializer

class TenantRoleViewSet(viewsets.ModelViewSet):
    queryset = TenantRole.objects.select_related("user", "lga")
    serializer_class = TenantRoleSerializer
    permission_classes = [IsAuthenticated, LGAAccessPermission]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_permissions(request):
    if not hasattr(request.user, "tenant_role"):
        return Response({"role": None, "lga": None, "permissions": []})
    role = request.user.tenant_role
    return Response({
        "role": role.role,
        "lga": str(role.lga) if role.lga else None,
        "can_access_all_lgas": role.can_access_all_lgas,
        "permissions": ["read", "write"] if role.role in ["state_admin", "super_admin"] else ["read", "write"]
    })