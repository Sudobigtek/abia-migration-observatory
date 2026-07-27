from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta


def command_center(request):
    """
    Leader-facing visual command center.
    Displays KPIs, recent xenophobia cases, partner status, and quick actions.
    """
    context = {
        "total_migrants": 0,
        "new_migrants_this_week": 0,
        "open_cases": 0,
        "xenophobia_cases": 0,
        "pending_referrals": 0,
        "ipfs_documents": 0,
        "recent_xenophobia_cases": [],
        "iom_last_report": None,
        "ncfrmi_last_report": None,
        "giz_last_report": None,
    }

    # Try to populate from actual models
    try:
        from abia.migrants.models import Migrant
        context["total_migrants"] = Migrant.objects.count()
        week_ago = timezone.now() - timedelta(days=7)
        context["new_migrants_this_week"] = Migrant.objects.filter(created_at__gte=week_ago).count()
    except Exception:
        pass

    try:
        from abia.cases.models import Case
        context["open_cases"] = Case.objects.exclude(status="resolved").count()
        # Assuming you add a case_type or tag for xenophobia; adjust as needed
        context["xenophobia_cases"] = Case.objects.filter(title__icontains="xenoph").count()
        context["recent_xenophobia_cases"] = Case.objects.filter(
            title__icontains="xenoph"
        ).select_related()[:5]
    except Exception:
        pass

    try:
        from abia.referrals.models import Referral
        context["pending_referrals"] = Referral.objects.filter(status="pending").count()
    except Exception:
        pass

    try:
        from abia.documents.models import Document
        context["ipfs_documents"] = Document.objects.filter(ipfs_hash__isnull=False).count()
    except Exception:
        pass

    return render(request, "dashboard/command_center.html", context)


def onboarding_landing(request):
    """Role-based onboarding entry point."""
    return render(request, "onboarding/landing.html")
