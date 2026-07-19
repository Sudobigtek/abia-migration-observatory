from django.contrib import admin
from .models import IPFSDocument

@admin.register(IPFSDocument)
class IPFSDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'doc_type', 'cid', 'migrant', 'uploaded_by', 'created_at']
    list_filter = ['doc_type', 'created_at']
    search_fields = ['title', 'cid']
