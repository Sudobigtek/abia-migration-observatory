"""Controller layer for public dashboard."""
import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import PublicFeedbackForm, MigrantRegistrationForm, StatusCheckForm
from .services import DashboardService, MapService
from .exceptions import FeedbackSubmissionError


def public_dashboard(request):
    """Render public-facing migration dashboard. No auth required."""
    context = DashboardService.get_dashboard_context()
    return render(request, "public_dashboard/dashboard.html", context)


def public_map_data(request):
    """Return GeoJSON data for public map."""
    geojson = MapService.get_geojson()
    return JsonResponse(geojson)


def public_feedback(request):
    """Handle public feedback form submission with security hardening."""
    from .security import HardenedFeedbackService

    if request.method == "GET":
        request.session["feedback_form_load_time"] = time.time()

    if request.method == "POST":
        form = PublicFeedbackForm(request.POST)
        if form.is_valid():
            try:
                session_data = {
                    "feedback_form_load_time": request.session.get(
                        "feedback_form_load_time"
                    )
                }
                result = HardenedFeedbackService.submit_feedback(
                    form.cleaned_data, request, session_data
                )
                if result["ambush_detected"]:
                    messages.warning(
                        request,
                        "Feedback received. Tracking ID: " + result["tracking_id"] +
                        ". SECURITY ALERT: Ambush indicators detected. " +
                        "Case flagged for immediate security review."
                    )
                elif result["requires_review"]:
                    messages.warning(
                        request,
                        "Feedback received. Tracking ID: " + result["tracking_id"] +
                        ". Your submission has been flagged for security review."
                    )
                else:
                    messages.success(
                        request,
                        "Thank you! Tracking ID: " + result["tracking_id"]
                    )
                return redirect("public_dashboard:feedback_success")
            except FeedbackSubmissionError as exc:
                messages.error(request, str(exc))
    else:
        form = PublicFeedbackForm()

    return render(request, "public_dashboard/feedback.html", {"form": form})


def feedback_success(request):
    """Render feedback submission success page."""
    return render(request, "public_dashboard/feedback_success.html")


def sdg_dashboard(request):
    """Render SDG alignment dashboard."""
    from .sdg import SDGCalculator
    return render(
        request,
        "public_dashboard/sdg_dashboard.html",
        {"sdg_data": SDGCalculator.calculate_all()}
    )


def migrant_register(request):
    """Handle migrant self-registration."""
    from .self_service import MigrantSelfService

    if request.method == "POST":
        form = MigrantRegistrationForm(request.POST)
        if form.is_valid():
            reg_id = MigrantSelfService.register_migrant(form.cleaned_data)
            messages.success(
                request,
                "Registration successful! Your ID: " + reg_id
            )
            return redirect("public_dashboard:registration_success")
    else:
        form = MigrantRegistrationForm()

    return render(
        request, "public_dashboard/migrant_register.html", {"form": form}
    )


def registration_success(request):
    """Render registration success page."""
    return render(request, "public_dashboard/registration_success.html")


def status_check(request):
    """Check case or registration status by tracking ID."""
    from .self_service import MigrantSelfService

    result = None
    if request.method == "POST":
        form = StatusCheckForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data["check_type"] == "case":
                result = MigrantSelfService.check_case_status(
                    data["tracking_id"]
                )
            else:
                result = MigrantSelfService.check_registration_status(
                    data["tracking_id"]
                )
            if not result:
                messages.error(request, "No record found with that ID.")
    else:
        form = StatusCheckForm()

    return render(
        request,
        "public_dashboard/status_check.html",
        {"form": form, "result": result}
    )

# ============================================
# NASA: Authenticated Dashboard View
# ============================================
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Command Center Dashboard'
        context['user'] = self.request.user
        return context

# ============================================
# NASA: Public Portal Landing (NO login required)
# ============================================
from django.views.generic import TemplateView

class PublicLandingView(TemplateView):
    template_name = 'public_dashboard/public_landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Abia Migration Observatory'
        return context

# ============================================
# NASA: Portal Views (public, no login)
# ============================================
from django.shortcuts import render

def check_status_view(request):
    return render(request, 'public_dashboard/check_status.html')

def odk_forms_view(request):
    return render(request, 'public_dashboard/odk_forms.html')

def feedback_success(request):
    return render(request, 'public_dashboard/feedback_success.html')

def registration_success(request):
    return render(request, 'public_dashboard/registration_success.html')


# NASA: Public portal landing
def portal(request):
    return render(request, "public_dashboard/public_landing.html")

def odk_forms(request):
    return render(request, "public_dashboard/odk_forms.html")

    return render(request, "public_dashboard/odk_forms.html")

# ============================================
# NASA: Data Collection Hub — Web Forms (NOT downloads)
# ============================================
from django.contrib import messages
from abia.data_collection.models import FormSubmission
from django.http import Http404
from django.utils import timezone

def data_collection_hub(request):
    """Landing page showing all available web forms."""
    form_types = [
        {
            'key': 'migration',
            'name': 'Migration Registration',
            'icon': 'bi-person-vcard',
            'color': 'primary',
            'desc': 'Register migrants, returnees, and IDPs entering Abia State.',
            'fields': 12,
        },
        {
            'key': 'trade',
            'name': 'Trade & Commerce',
            'icon': 'bi-shop',
            'color': 'success',
            'desc': 'Collect trade data, cross-border commerce, and SME activity.',
            'fields': 10,
        },
        {
            'key': 'sports',
            'name': 'Sports & Youth',
            'icon': 'bi-trophy',
            'color': 'warning',
            'desc': 'Track youth sports programs, talent identification, and events.',
            'fields': 8,
        },
        {
            'key': 'hotspot',
            'name': 'Hotspot Monitoring',
            'icon': 'bi-geo-alt',
            'color': 'danger',
            'desc': 'Report migration hotspots, incidents, and security alerts.',
            'fields': 9,
        },
        {
            'key': 'returnee',
            'name': 'Returnee Assessment',
            'icon': 'bi-house-check',
            'color': 'info',
            'desc': 'Assess returning migrants for reintegration support.',
            'fields': 15,
        },
        {
            'key': 'general',
            'name': 'General Data',
            'icon': 'bi-clipboard-data',
            'color': 'secondary',
            'desc': 'Flexible form for any other data collection needs.',
            'fields': 6,
        },
    ]
    recent_submissions = FormSubmission.objects.all()[:5]
    return render(request, 'public_dashboard/data_collection_hub.html', {
        'form_types': form_types,
        'recent_submissions': recent_submissions,
        'total_submissions': FormSubmission.objects.count(),
    })

def collect_form(request, form_type):
    """Generic web form handler for all data types."""
    valid_types = dict(FormSubmission.FORM_TYPES)
    if form_type not in valid_types:
        raise Http404("Form type not found")
    
    if request.method == 'POST':
        data = dict(request.POST)
        # Remove CSRF token from stored data
        data.pop('csrfmiddlewaretoken', None)
        # Convert single-item lists to strings
        for key in data:
            if len(data[key]) == 1:
                data[key] = data[key][0]
        
        submission = FormSubmission.objects.create(
            form_type=form_type,
            title=data.get('title', f'{valid_types[form_type]} — {timezone.now().strftime("%Y-%m-%d %H:%M")}'),
            data=data,
            source_ip=request.META.get('REMOTE_ADDR'),
        )
        messages.success(request, f"{valid_types[form_type]} submitted successfully. Reference: #{submission.id}")
        return redirect('public_dashboard:data_collection_hub')
    
    return render(request, f'public_dashboard/collect_{form_type}.html', {
        'form_type': form_type,
        'form_name': valid_types[form_type],
    })

def submission_list(request):
    """View all submissions — admin-facing table."""
    submissions = FormSubmission.objects.all()[:100]
    return render(request, 'public_dashboard/submission_list.html', {
        'submissions': submissions,
    })

# ============================================
# NASA: Analytics Dashboard with Charts
# ============================================
from django.db.models import Count
from collections import Counter

def analytics_dashboard(request):
    """Public analytics page with Chart.js visualizations."""
    submissions = FormSubmission.objects.all()
    
    # Form type distribution
    type_counts = dict(submissions.values('form_type').annotate(count=Count('form_type')).values_list('form_type', 'count'))
    type_labels = [dict(FormSubmission.FORM_TYPES).get(k, k) for k in type_counts.keys()]
    type_data = list(type_counts.values())
    
    # Submissions over time (last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    dates = []
    daily_counts = []
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = submissions.filter(created_at__date=date).count()
        dates.append(date.strftime('%a %d'))
        daily_counts.append(count)
    
    # LGA distribution from migration data
    lga_counts = Counter()
    for sub in submissions.filter(form_type='migration'):
        lga = sub.data.get('lga', 'Unknown')
        lga_counts[lga] += 1
    
    top_lgas = dict(lga_counts.most_common(8))
    
    # Sync status
    synced_ncfrmi = submissions.filter(synced_to_ncfrmi=True).count()
    synced_iom = submissions.filter(synced_to_iom=True).count()
    pending = submissions.count() - max(synced_ncfrmi, synced_iom)
    
    context = {
        'total_submissions': submissions.count(),
        'type_labels': type_labels,
        'type_data': type_data,
        'dates': dates,
        'daily_counts': daily_counts,
        'lga_labels': list(top_lgas.keys()),
        'lga_data': list(top_lgas.values()),
        'synced_ncfrmi': synced_ncfrmi,
        'synced_iom': synced_iom,
        'pending': pending,
    }
    return render(request, 'public_dashboard/analytics.html', context)
