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
