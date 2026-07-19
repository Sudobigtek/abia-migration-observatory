from rest_framework import serializers
from .models import IPFSDocument, PinQueue

class IPFSDocumentSerializer(serializers.ModelSerializer):
    migrant_name = serializers.CharField(source='migrant.full_name', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True)
    uploader_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    class Meta:
        model = IPFSDocument
        fields = [
            'id', 'title', 'doc_type', 'description', 'cid', 'ipfs_gateway_url',
            'pin_status', 'file_size', 'mime_type', 'local_file',
            'migrant', 'migrant_name', 'case', 'case_title', 'uploaded_by', 'uploader_name',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'cid', 'ipfs_gateway_url', 'pin_status', 'created_at', 'updated_at']

class IPFSDocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    class Meta:
        model = IPFSDocument
        fields = ['title', 'doc_type', 'description', 'file', 'migrant', 'case']

class PinQueueSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    class Meta:
        model = PinQueue
        fields = ['id', 'document', 'document_title', 'status', 'attempts', 'last_error', 'scheduled_at', 'completed_at', 'created_at']
        read_only_fields = ['id', 'created_at']
