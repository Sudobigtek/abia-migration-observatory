from rest_framework import viewsets
from .serializers import MigrantSerializer
from .services import MigrantService
from common.pagination import StandardResultsSetPagination
from common.permissions import LGAAccessPermission


class MigrantViewSet(viewsets.ModelViewSet):
    serializer_class = MigrantSerializer
    permission_classes = [LGAAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return MigrantService.get_migrants_for_request(self.request)

    def perform_create(self, serializer):
        MigrantService.create_migrant(serializer.validated_data, self.request.user)

    def perform_update(self, serializer):
        MigrantService.get_migrant_by_id(self.kwargs["pk"], self.request.user)
        serializer.save()

    def perform_destroy(self, instance):
        MigrantService.get_migrant_by_id(instance.id, self.request.user)
        instance.delete()
