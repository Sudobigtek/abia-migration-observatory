from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from .models import (CertifiedVolunteer, CountryCluster, CorpsLeadership,
    WelfareContact, ActivityLog, EthicsComplaint, TrainingModule, DiasporaPartner)

def corps_dashboard(request):
    total_volunteers = CertifiedVolunteer.objects.filter(is_active=True).count()
    certified = CertifiedVolunteer.objects.filter(status='certified', is_active=True).count()
    clusters = CountryCluster.objects.filter(active_status=True).count()
    contacts_month = WelfareContact.objects.filter(
        contact_date__year=timezone.now().year,
        contact_date__month=timezone.now().month
    ).count()
    pending_ethics = EthicsComplaint.objects.filter(status__in=['pending', 'under_investigation']).count()
    leadership = CorpsLeadership.objects.filter(is_active=True).select_related('volunteer')
    recent_contacts = WelfareContact.objects.select_related('volunteer').order_by('-contact_date')[:5]
    recent_complaints = EthicsComplaint.objects.select_related('respondent').order_by('-created_at')[:3]
    clusters_list = CountryCluster.objects.filter(active_status=True).select_related('coordinator')[:10]
    partners = DiasporaPartner.objects.filter(is_active=True)[:6]

    context = {
        'total_volunteers': total_volunteers,
        'certified': certified,
        'clusters': clusters,
        'contacts_month': contacts_month,
        'pending_ethics': pending_ethics,
        'leadership': leadership,
        'recent_contacts': recent_contacts,
        'recent_complaints': recent_complaints,
        'clusters_list': clusters_list,
        'partners': partners,
    }
    return render(request, 'migration_corps/dashboard.html', context)

def volunteer_list(request):
    volunteers = CertifiedVolunteer.objects.filter(is_active=True)
    country = request.GET.get('country')
    status = request.GET.get('status')
    if country:
        volunteers = volunteers.filter(country__iexact=country)
    if status:
        volunteers = volunteers.filter(status=status)
    countries = CertifiedVolunteer.objects.filter(is_active=True).values_list('country', flat=True).distinct()
    context = {
        'volunteers': volunteers,
        'countries': countries,
        'status_choices': CertifiedVolunteer.STATUS_CHOICES,
    }
    return render(request, 'migration_corps/volunteer_list.html', context)

def volunteer_detail(request, pk):
    volunteer = get_object_or_404(CertifiedVolunteer, pk=pk)
    logs = volunteer.activity_logs.order_by('-year', '-month')[:6]
    contacts = volunteer.welfare_contacts.order_by('-contact_date')[:5]
    progress = volunteer.training_progress.select_related('module').order_by('module__module_number')
    return render(request, 'migration_corps/volunteer_detail.html', {
        'volunteer': volunteer, 'logs': logs, 'contacts': contacts, 'progress': progress
    })

def verify_volunteer(request):
    result = None
    cert_num = request.GET.get('cert')
    if cert_num:
        try:
            vol = CertifiedVolunteer.objects.get(certification_number=cert_num, is_active=True)
            result = vol
        except CertifiedVolunteer.DoesNotExist:
            result = 'invalid'
    return render(request, 'migration_corps/verify_volunteer.html', {'result': result, 'cert_num': cert_num})
