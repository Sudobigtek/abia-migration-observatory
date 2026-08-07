from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import (
    Sector, Occupation, EmbassyMission, ForeignEmployer, Vacancy,
    TalentPool, Deployment, CredentialEndorsement, WelfareCheck,
    GrievanceTicket, TransparencyReport
)

def atevs_dashboard(request):
    total_candidates = TalentPool.objects.filter(is_active=True).count()
    open_vacancies = Vacancy.objects.filter(status='open', is_active=True).count()
    deployed = Deployment.objects.count()
    endorsed = CredentialEndorsement.objects.filter(is_revoked=False).count()
    missions = EmbassyMission.objects.filter(mou_signed=True, is_active=True).count()
    employers_verified = ForeignEmployer.objects.filter(embassy_verified=True, is_active=True).count()
    open_grievances = GrievanceTicket.objects.filter(status__in=['open','investigating']).count()
    
    recent_vacancies = Vacancy.objects.filter(is_active=True).select_related('employer').order_by('-posted_date')[:6]
    recent_deployments = Deployment.objects.select_related('candidate','vacancy__employer').order_by('-deployment_date')[:5]
    top_employers = ForeignEmployer.objects.filter(is_active=True).order_by('-compliance_score')[:6]
    
    context = {
        'total_candidates': total_candidates,
        'open_vacancies': open_vacancies,
        'deployed': deployed,
        'endorsed': endorsed,
        'missions': missions,
        'employers_verified': employers_verified,
        'open_grievances': open_grievances,
        'recent_vacancies': recent_vacancies,
        'recent_deployments': recent_deployments,
        'top_employers': top_employers,
    }
    return render(request, 'talent_exchange/dashboard.html', context)

def transparency_public(request):
    report = TransparencyReport.objects.order_by('-snapshot_date').first()
    employers = ForeignEmployer.objects.filter(is_active=True, embassy_verified=True).order_by('-compliance_score')[:15]
    destinations = {}
    sectors = {}
    if report:
        destinations = report.workers_by_destination
        sectors = report.workers_by_sector
    
    context = {
        'report': report,
        'employers': employers,
        'destinations': destinations,
        'sectors': sectors,
    }
    return render(request, 'talent_exchange/transparency.html', context)

def verify_endorsement(request):
    from .models import CredentialEndorsement
    result = None
    endorsement_num = request.GET.get('endorsement')
    if endorsement_num:
        try:
            result = CredentialEndorsement.objects.get(endorsement_number=endorsement_num)
        except CredentialEndorsement.DoesNotExist:
            result = 'invalid'
    return render(request, 'talent_exchange/verify_endorsement.html', {'result': result, 'endorsement_num': endorsement_num})

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True, status='open').select_related('employer','occupation').order_by('-posted_date')
    sector = request.GET.get('sector')
    country = request.GET.get('country')
    if sector:
        vacancies = vacancies.filter(occupation__sector__code__iexact=sector)
    if country:
        vacancies = vacancies.filter(employer__country__iexact=country)
    
    sectors = Sector.objects.filter(is_active=True)
    countries = ForeignEmployer.objects.filter(is_active=True).values_list('country', flat=True).distinct()
    
    context = {
        'vacancies': vacancies,
        'sectors': sectors,
        'countries': countries,
    }
    return render(request, 'talent_exchange/vacancy_list.html', context)

def employer_list(request):
    employers = ForeignEmployer.objects.filter(is_active=True).order_by('-compliance_score')
    tier = request.GET.get('tier')
    if tier:
        employers = employers.filter(compliance_tier=tier)
    context = {
        'employers': employers,
        'tier_choices': ForeignEmployer.COMPLIANCE_TIER,
    }
    return render(request, 'talent_exchange/employer_list.html', context)
