from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LGA

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Abia Observatory', {'fields': ('role', 'phone')}),
    )

@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'user_count', 'case_count', 'migrant_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['user_count', 'case_count', 'migrant_count']
