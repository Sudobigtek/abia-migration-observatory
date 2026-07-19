from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentCategory
from rest_framework import serializers

class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description', 'allowed_extensions', 'max_file_size_mb', 'requires_approval', 'created_at']

class DocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'title', 'category', 'category_name', 'file', 'file_size', 'mime_type', 'description', 'status', 'uploaded_by', 'uploaded_by_name', 'version', 'tags', 'created_at']
        read_only_fields = ['id', 'file_size', 'uploaded_by', 'created_at']

class DocumentCategoryViewSet(viewsets.ModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'uploaded_by']

    def get_queryset(self):
        return Document.objects.select_related('category', 'uploaded_by')

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        file_size = file.size if file else 0
        serializer.save(uploaded_by=self.request.user, file_size=file_size)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        doc = self.get_object()
        if doc.status != 'pending_approval':
            return Response({'error': 'Document not pending approval'}, status=400)
        doc.status = 'approved'
        doc.approved_by = request.user
        from django.utils import timezone
        doc.approved_at = timezone.now()
        doc.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        doc = self.get_object()
        doc.status = 'rejected'
        doc.save()
        return Response({'status': 'rejected'})
