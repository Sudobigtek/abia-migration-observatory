from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


def _safe_count(queryset):
    """Return count or 0 if the query fails for any reason."""
    try:
        return queryset.count()
    except Exception:
        return 0


def _get_models():
    """Safely import models so missing apps do not crash the page."""
    Migrant = Case = Referral = None
    try:
        from abia.migrants.models import Migrant
    except Exception:
        pass
    try:
        from abia.cases.models import Case
    except Exception:
        pass
    try:
        from abia.referrals.models import Referral
    except Exception:
        pass
    return Migrant, Case, Referral


def public_dashboard(request):
    """
    Public-facing dashboard (no login required).
    Shows high-level live stats only.
    """
    Migrant, Case, Referral = _get_models()
    week_ago = timezone.now() - timedelta(days=7)

    context = {
        "total_migrants": _safe_count(Migrant.objects.all()) if Migrant else 0,
        "total_cases": _safe_count(Case.objects.all()) if Case else 0,
        "open_cases": _safe_count(Case.objects.filter(status="open")) if Case else 0,
        "resolved_cases": _safe_count(Case.objects.filter(status__in=["resolved", "closed"])) if Case else 0,
        "new_this_week": _safe_count(Migrant.objects.filter(created_at__gte=week_ago)) if Migrant else 0,
    }
    return render(request, "public_dashboard/dashboard.html", context)


@login_required
def command_center(request):
    """
    Authenticated Command Center for state officers.
    Live KPIs + LGA breakdown.
    """
    Migrant, Case, Referral = _get_models()
    week_ago = timezone.now() - timedelta(days=7)

    context = {
        "total_migrants": _safe_count(Migrant.objects.all()) if Migrant else 0,
        "new_migrants_this_week": _safe_count(Migrant.objects.filter(created_at__gte=week_ago)) if Migrant else 0,
        "open_cases": _safe_count(Case.objects.exclude(status__in=["resolved", "closed"])) if Case else 0,
        "high_priority_cases": _safe_count(Case.objects.filter(priority__in=["high", "critical"])) if Case else 0,
        "pending_referrals": _safe_count(Referral.objects.filter(status="pending")) if Referral else 0,
        "lga_breakdown": [],
        "recent_cases": [],
    }

    # LGA breakdown (uses the safest available field)
    if Migrant:
        try:
            context["lga_breakdown"] = list(
                Migrant.objects.values("current_lga_text")
                .annotate(count=Count("id"))
                .order_by("-count")[:12]
            )
        except Exception:
            try:
                context["lga_breakdown"] = list(
                    Migrant.objects.values("lga__name")
                    .annotate(count=Count("id"))
                    .order_by("-count")[:12]
                )
            except Exception:
                pass

    if Case:
        try:
            context["recent_cases"] = list(
                Case.objects.select_related()
                .order_by("-created_at")[:8]
            )
        except Exception:
            pass

    return render(request, "dashboard/command_center.html", context)


@login_required
def dashboard(request):
    """
    Simple authenticated dashboard (alias used by some older links).
    """
    return command_center(request)
