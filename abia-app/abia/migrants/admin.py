from django.contrib import admin
from .models import Migrant

@admin.register(Migrant)
class MigrantAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'gender', 'phone', 'current_lga', 'status', 'created_at']
    list_filter = ['status', 'gender', 'created_at']
    search_fields = ['full_name', 'phone', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='Mark selected migrants as active')
    def mark_active(self, request, queryset):
        queryset.update(status='active')

    @admin.action(description='Mark selected migrants as inactive')
    def mark_inactive(self, request, queryset):
        queryset.update(status='inactive')
