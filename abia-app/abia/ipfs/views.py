from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import IPFSDocument, PinQueue
from .serializers import IPFSDocumentSerializer, IPFSDocumentUploadSerializer, PinQueueSerializer

class IPFSDocumentViewSet(viewsets.ModelViewSet):
    queryset = IPFSDocument.objects.select_related('migrant', 'case', 'uploaded_by')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['doc_type', 'pin_status', 'migrant', 'case']
    search_fields = ['title', 'description', 'cid']
    ordering_fields = ['created_at', 'file_size']

    def get_serializer_class(self):
        if self.action == 'create':
            return IPFSDocumentUploadSerializer
        return IPFSDocumentSerializer

    def perform_create(self, serializer):
        doc = serializer.save(uploaded_by=self.request.user, pin_status='pending')
        PinQueue.objects.create(document=doc, status='queued')

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        doc = self.get_object()
        if doc.pin_status == 'pinned':
            return Response({'status': 'already_pinned'})
        doc.pin_status = 'pinned'
        doc.cid = f"QmPlaceholder{doc.id.hex[:16]}"
        doc.ipfs_gateway_url = f"https://ipfs.io/ipfs/{doc.cid}"
        doc.save()
        queue, _ = PinQueue.objects.get_or_create(document=doc)
        queue.status = 'completed'
        import django.utils.timezone
        queue.completed_at = django.utils.timezone.now()
        queue.save()
        return Response({'status': 'pinned', 'cid': doc.cid})

    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        doc = self.get_object()
        doc.pin_status = 'removed'
        doc.cid = ''
        doc.ipfs_gateway_url = ''
        doc.save()
        return Response({'status': 'unpinned'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count, Sum
        return Response({
            'total': IPFSDocument.objects.count(),
            'by_type': dict(IPFSDocument.objects.values('doc_type').annotate(count=Count('id')).values_list('doc_type', 'count')),
            'by_status': dict(IPFSDocument.objects.values('pin_status').annotate(count=Count('id')).values_list('pin_status', 'count')),
            'total_size': IPFSDocument.objects.aggregate(total=Sum('file_size'))['total'] or 0,
            'pending_pins': PinQueue.objects.filter(status='queued').count(),
        })

class PinQueueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PinQueue.objects.select_related('document')
    serializer_class = PinQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'attempts']

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        queue = self.get_object()
        if queue.status not in ['failed', 'queued']:
            return Response({'error': 'Cannot retry'}, status=status.HTTP_400_BAD_REQUEST)
        queue.status = 'queued'
        queue.attempts += 1
        queue.last_error = ''
        queue.save()
        return Response({'status': 'requeued'})
