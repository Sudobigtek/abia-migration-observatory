from django.shortcuts import render
from django.db.models import Count
from abia.migrants.models import Migrant
from abia.cases.models import Case

def dashboard(request):
    context = {
        'total_migrants': Migrant.objects.count(),
        'total_cases': Case.objects.count(),
        'open_cases': Case.objects.filter(status='open').count(),
        'high_priority_cases': Case.objects.filter(priority='high').count(),
        'lga_breakdown': list(Migrant.objects.values('current_lga_text').annotate(count=Count('id')).order_by('-count')[:10]),
    }
    return render(request, 'dashboard.html', context)
