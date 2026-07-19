from django.contrib import admin
from .models import Case

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['case_type', 'status', 'priority', 'migrant', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'case_type', 'created_at']
    search_fields = ['description', 'migrant__full_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    actions = ['mark_resolved', 'mark_escalated']

    @admin.action(description='Mark selected cases as resolved')
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')

    @admin.action(description='Mark selected cases as escalated')
    def mark_escalated(self, request, queryset):
        queryset.update(status='escalated')
