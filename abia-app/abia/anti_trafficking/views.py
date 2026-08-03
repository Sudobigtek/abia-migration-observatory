from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import VictimIntake, Shelter, CourtCase, CommunityAwarenessEvent


@login_required
def dashboard(request):
    context = {
        'total_victims': VictimIntake.objects.count(),
        'total_shelters': Shelter.objects.count(),
        'total_cases': CourtCase.objects.count(),
        'total_events': CommunityAwarenessEvent.objects.count(),
        'recent_victims': VictimIntake.objects.order_by('-intake_date')[:10],
    }
    return render(request, 'anti_trafficking/dashboard.html', context)
