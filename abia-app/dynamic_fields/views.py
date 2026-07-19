from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import DynamicFieldDefinition, EntityDynamicData
from .serializers import (
    DynamicFieldDefinitionSerializer,
    EntityDynamicDataSerializer,
    EntityDynamicDataCreateSerializer,
    BulkDynamicDataSerializer
)


class DynamicFieldDefinitionViewSet(viewsets.ModelViewSet):
    queryset = DynamicFieldDefinition.objects.select_related('created_by')
    serializer_class = DynamicFieldDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['entity_type', 'field_type', 'is_required', 'is_active']
    search_fields = ['field_name', 'field_label', 'help_text']
    ordering_fields = ['order', 'created_at', 'field_name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_entity(self, request):
        entity_type = request.query_params.get('entity_type')
        if not entity_type:
            return Response({'error': 'entity_type required'}, status=status.HTTP_400_BAD_REQUEST)
        defs = self.get_queryset().filter(entity_type=entity_type, is_active=True)
        return Response(self.get_serializer(defs, many=True).data)


class EntityDynamicDataViewSet(viewsets.ModelViewSet):
    queryset = EntityDynamicData.objects.select_related('field_definition')
    serializer_class = EntityDynamicDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['entity_type', 'entity_id', 'field_definition']
    search_fields = ['value_text']
    ordering_fields = ['created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EntityDynamicDataCreateSerializer
        return EntityDynamicDataSerializer

    @action(detail=False, methods=['get'])
    def for_entity(self, request):
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')
        if not entity_type or not entity_id:
            return Response({'error': 'entity_type and entity_id required'}, status=status.HTTP_400_BAD_REQUEST)
        data = self.get_queryset().filter(entity_type=entity_type, entity_id=entity_id)
        return Response(self.get_serializer(data, many=True).data)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        serializer = BulkDynamicDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entity_type = serializer.validated_data['entity_type']
        entity_id = serializer.validated_data['entity_id']
        fields = serializer.validated_data['fields']

        created, updated, errors = [], [], []

        for field_data in fields:
            field_def_id = field_data.get('field_definition')
            if not field_def_id:
                errors.append({'error': 'field_definition ID missing', 'data': field_data})
                continue
            try:
                field_def = DynamicFieldDefinition.objects.get(id=field_def_id, entity_type=entity_type)
            except DynamicFieldDefinition.DoesNotExist:
                errors.append({'error': f'Field definition {field_def_id} not found', 'data': field_data})
                continue

            value_field = {
                'text': 'value_text', 'textarea': 'value_text',
                'number': 'value_number', 'integer': 'value_number',
                'boolean': 'value_boolean', 'checkbox': 'value_boolean',
                'date': 'value_date', 'datetime': 'value_date',
                'json': 'value_json', 'select': 'value_text',
            }.get(field_def.field_type, 'value_text')

            defaults = {'value_text': None, 'value_number': None, 'value_boolean': None, 'value_date': None, 'value_json': None}
            defaults[value_field] = field_data.get('value')

            obj, was_created = EntityDynamicData.objects.update_or_create(
                entity_type=entity_type, entity_id=entity_id, field_definition=field_def, defaults=defaults
            )
            (created if was_created else updated).append(str(obj.id))

        return Response({'created': len(created), 'updated': len(updated), 'errors': errors, 'created_ids': created, 'updated_ids': updated})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from django.db.models import Count
        return Response({
            'total_definitions': DynamicFieldDefinition.objects.count(),
            'total_data_entries': EntityDynamicData.objects.count(),
            'by_entity_type': dict(DynamicFieldDefinition.objects.values('entity_type').annotate(count=Count('id')).values_list('entity_type', 'count')),
            'active_definitions': DynamicFieldDefinition.objects.filter(is_active=True).count(),
        })
