from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from abia.accounts.models import LGA
from abia.anti_trafficking.models import (
    VictimIntake, Shelter, CommunityAwarenessEvent, CourtCase,
)


@login_required
def lga_dashboard(request):
    try:
        assigned_lga = request.user.userprofile.assigned_lga
    except Exception:
        assigned_lga = None

    if not assigned_lga:
        return render(request, "lga_portal/no_access.html", {"message": "No LGA assigned to your account."})

    lga = LGA.objects.filter(name=assigned_lga).first()
    if not lga:
        return render(request, "lga_portal/no_access.html", {"message": f"LGA '{assigned_lga}' not found."})

    context = {
        "lga": lga,
        "victim_count": VictimIntake.objects.filter(current_lga=lga).count(),
        "shelter_count": Shelter.objects.filter(lga=lga).count(),
        "event_count": CommunityAwarenessEvent.objects.filter(lga=lga).count(),
        "case_count": CourtCase.objects.filter(court_location=lga).count(),
        "recent_victims": VictimIntake.objects.filter(current_lga=lga).order_by('-intake_date')[:5],
    }
    return render(request, "lga_portal/dashboard.html", context)


@login_required
def lga_victims(request):
    try:
        assigned_lga = request.user.userprofile.assigned_lga
    except Exception:
        assigned_lga = None
    lga = LGA.objects.filter(name=assigned_lga).first()
    victims = VictimIntake.objects.filter(current_lga=lga).order_by('-intake_date') if lga else []
    return render(request, "lga_portal/victims.html", {"lga": lga, "victims": victims})


@login_required
def lga_shelters(request):
    try:
        assigned_lga = request.user.userprofile.assigned_lga
    except Exception:
        assigned_lga = None
    lga = LGA.objects.filter(name=assigned_lga).first()
    shelters = Shelter.objects.filter(lga=lga) if lga else []
    return render(request, "lga_portal/shelters.html", {"lga": lga, "shelters": shelters})


@login_required
def lga_cases(request):
    try:
        assigned_lga = request.user.userprofile.assigned_lga
    except Exception:
        assigned_lga = None
    lga = LGA.objects.filter(name=assigned_lga).first()
    cases = CourtCase.objects.filter(court_location=lga).order_by('-next_hearing_date') if lga else []
    return render(request, "lga_portal/cases.html", {"lga": lga, "cases": cases})


@login_required
def lga_events(request):
    try:
        assigned_lga = request.user.userprofile.assigned_lga
    except Exception:
        assigned_lga = None
    lga = LGA.objects.filter(name=assigned_lga).first()
    events = CommunityAwarenessEvent.objects.filter(lga=lga).order_by('-date') if lga else []
    return render(request, "lga_portal/events.html", {"lga": lga, "events": events})
