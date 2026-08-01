from django.contrib import admin
from .models import FormSubmission

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form_type', 'title', 'submitted_by', 'created_at', 'synced_to_ncfrmi', 'synced_to_iom']
    list_filter = ['form_type', 'synced_to_ncfrmi', 'synced_to_iom', 'created_at']
    search_fields = ['title', 'data']
    date_hierarchy = 'created_at'
