from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import WorkflowDefinition, WorkflowInstance, WorkflowStep
from rest_framework import serializers

class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowDefinition
        fields = ['id', 'name', 'description', 'model_name', 'steps', 'is_active', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)

    class Meta:
        model = WorkflowInstance
        fields = ['id', 'workflow', 'workflow_name', 'object_type', 'object_id', 'current_step', 'status', 'assigned_to', 'started_at', 'completed_at']
        read_only_fields = ['id', 'started_at']

class WorkflowDefinitionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowDefinition.objects.select_related('created_by')
    serializer_class = WorkflowDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'workflow', 'assigned_to']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['super_admin', 'state_admin']:
            return WorkflowInstance.objects.all()
        return WorkflowInstance.objects.filter(assigned_to=user)

    @action(detail=True, methods=['post'])
    def advance(self, request, pk=None):
        instance = self.get_object()
        if instance.status == 'completed':
            return Response({'error': 'Workflow already completed'}, status=400)
        instance.current_step += 1
        if instance.current_step >= len(instance.workflow.steps):
            instance.status = 'completed'
            from django.utils import timezone
            instance.completed_at = timezone.now()
        instance.save()
        return Response({'status': 'advanced', 'current_step': instance.current_step})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'cancelled'
        instance.save()
        return Response({'status': 'cancelled'})
