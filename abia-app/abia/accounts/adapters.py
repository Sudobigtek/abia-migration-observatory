from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_staff = False
        if commit:
            user.save()
            public_group, _ = Group.objects.get_or_create(name='Public')
            user.groups.add(public_group)
        return user

    def get_login_redirect_url(self, request):
        user = request.user
        if user.groups.filter(name='Admin').exists() or user.is_superuser:
            return '/dashboard/'
        elif user.groups.filter(name='LGA Officer').exists():
            return '/lga-portal/'
        elif user.groups.filter(name='Investigator').exists():
            return '/anti-trafficking/'
        elif user.groups.filter(name='Public').exists():
            return '/public-dashboard/'
        return '/public-dashboard/'
