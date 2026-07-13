from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ReferralSerializer
from .services import ReferralService
from common.pagination import StandardResultsSetPagination
from common.permissions import LGAAccessPermission


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [LGAAccessPermission]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ReferralService.get_referrals_for_request(self.request)

    def perform_create(self, serializer):
        ReferralService.create_referral(serializer.validated_data, self.request.user)

    def perform_update(self, serializer):
        ReferralService.get_referral_by_id(self.kwargs["pk"], self.request.user)
        serializer.save()

    def perform_destroy(self, instance):
        ReferralService.get_referral_by_id(instance.id, self.request.user)
        instance.delete()

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        new_status = request.data.get("status")
        referral = ReferralService.transition_referral(pk, new_status, request.user)
        serializer = self.get_serializer(referral)
        return Response(serializer.data)
