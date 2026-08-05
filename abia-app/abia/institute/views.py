from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg
from django.utils import timezone
from .models import CourseCatalog, Cohort, StudentEnrollment, PartnerInstitution, CertificateVerification

def institute_dashboard(request):
    total_courses = CourseCatalog.objects.filter(is_active=True).count()
    total_cohorts = Cohort.objects.filter(status__in=['active', 'enrolling']).count()
    total_students = StudentEnrollment.objects.filter(status='active').count()
    total_certificates = CertificateVerification.objects.filter(is_valid=True).count()
    partners = PartnerInstitution.objects.filter(is_active=True, mou_signed=True).count()
    recent_cohorts = Cohort.objects.select_related('course').order_by('-start_date')[:6]
    courses = CourseCatalog.objects.filter(is_active=True)[:6]

    context = {
        'total_courses': total_courses,
        'total_cohorts': total_cohorts,
        'total_students': total_students,
        'total_certificates': total_certificates,
        'partners': partners,
        'recent_cohorts': recent_cohorts,
        'courses': courses,
    }
    return render(request, 'institute/dashboard.html', context)

def course_list(request):
    courses = CourseCatalog.objects.filter(is_active=True)
    return render(request, 'institute/course_list.html', {'courses': courses})

def verify_certificate(request):
    result = None
    cert_number = request.GET.get('cert')
    if cert_number:
        try:
            cert = CertificateVerification.objects.get(certificate_number=cert_number, is_valid=True)
            cert.verified_count += 1
            cert.last_verified = timezone.now()
            cert.save()
            result = cert
        except CertificateVerification.DoesNotExist:
            result = 'invalid'
    return render(request, 'institute/verify.html', {'result': result, 'cert_number': cert_number})
