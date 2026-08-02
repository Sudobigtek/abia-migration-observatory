from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from abia.accounts.models import UserProfile, LGA

User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'LGA Assignment'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'lga':
            kwargs['queryset'] = LGA.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
