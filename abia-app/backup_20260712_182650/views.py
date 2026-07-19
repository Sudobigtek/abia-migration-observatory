from rest_framework import viewsets
from .serializers import UserSerializer, LGASerializer
from .services import UserService, LGAService
from abia.common.pagination import StandardResultsSetPagination
from abia.common.permissions import LGAAccessPermission


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [LGAAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return UserService.get_users_for_request(self.request)

    def perform_create(self, serializer):
        UserService.create_user(serializer.validated_data, self.request.user)

    def perform_update(self, serializer):
        UserService.get_by_id(self.kwargs["pk"], self.request.user)
        serializer.save()

    def perform_destroy(self, instance):
        UserService.get_by_id(instance.id, self.request.user)
        instance.delete()


class LGAViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LGASerializer
    permission_classes = [LGAAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return LGAService.get_all_lgas()
