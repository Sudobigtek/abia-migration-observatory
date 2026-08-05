
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Beneficiary, PillarParticipation, ProgramOutcomeSnapshot, PolicyEvidence, StakeholderEngagement

def dashboard(request):
    total_beneficiaries = Beneficiary.objects.filter(is_active=True).count()
    status_counts = dict(Beneficiary.objects.filter(is_active=True).values("current_status").annotate(count=Count("id")).values_list("current_status", "count"))
    location_counts = dict(Beneficiary.objects.filter(is_active=True).values("current_location_category").annotate(count=Count("id")).values_list("current_location_category", "count"))
    gender_counts = dict(Beneficiary.objects.filter(is_active=True).values("gender").annotate(count=Count("id")).values_list("gender", "count"))
    sector_counts = dict(Beneficiary.objects.filter(is_active=True).exclude(skill_sector="").values("skill_sector").annotate(count=Count("id")).values_list("skill_sector", "count"))

    p1_counseling = PillarParticipation.objects.filter(pillar="p1").aggregate(
        total=Count("id"), completed=Count("id", filter=Q(completed_date__isnull=False)),
        regular_pathway=Count("id", filter=Q(migration_pathway__in=["student_visa","skilled_worker","family_reunion","business_visa"])),
        irregular_pathway=Count("id", filter=Q(migration_pathway="irregular")), referrals=Count("id", filter=Q(protection_referral_made=True)),
    )
    p2_language = PillarParticipation.objects.filter(pillar="p2").aggregate(
        total=Count("id"), cultural_completed=Count("id", filter=Q(cultural_orientation_completed=True)), avg_readiness=Avg("integration_readiness_score"),
    )
    p3_skills = PillarParticipation.objects.filter(pillar="p3").aggregate(
        total=Count("id"), certified=Count("id", filter=Q(certification_issued=True)),
        placed_employed=Count("id", filter=Q(placement_status="employed_domestic")),
        placed_self=Count("id", filter=Q(placement_status="self_employed")), placed_abroad=Count("id", filter=Q(placement_status="employed_abroad")),
    )
    p4_reint = PillarParticipation.objects.filter(pillar="p4").aggregate(
        total=Count("id"), packages_delivered=Count("id", filter=Q(reintegration_package_delivered=True)),
        micro_enterprises=Count("id", filter=Q(micro_enterprise_registered=True)), alumni=Count("id", filter=Q(alumni_network_member=True)),
    )

    latest_snapshot = ProgramOutcomeSnapshot.objects.first()
    recent_evidence = PolicyEvidence.objects.filter(is_published=True)[:5]
    recent_engagements = StakeholderEngagement.objects.all()[:5]

    context = {
        "total_beneficiaries": total_beneficiaries, "status_counts": status_counts,
        "location_counts": location_counts, "gender_counts": gender_counts,
        "sector_counts": sector_counts, "p1_metrics": p1_counseling,
        "p2_metrics": p2_language, "p3_metrics": p3_skills, "p4_metrics": p4_reint,
        "latest_snapshot": latest_snapshot, "recent_evidence": recent_evidence,
        "recent_engagements": recent_engagements,
    }
    return render(request, "japa_development/dashboard.html", context)

def beneficiary_list(request):
    beneficiaries = Beneficiary.objects.filter(is_active=True)
    status = request.GET.get("status")
    location = request.GET.get("location")
    sector = request.GET.get("sector")
    gender = request.GET.get("gender")
    lga = request.GET.get("lga")
    if status: beneficiaries = beneficiaries.filter(current_status=status)
    if location: beneficiaries = beneficiaries.filter(current_location_category=location)
    if sector: beneficiaries = beneficiaries.filter(skill_sector=sector)
    if gender: beneficiaries = beneficiaries.filter(gender=gender)
    if lga: beneficiaries = beneficiaries.filter(lga__icontains=lga)

    context = {
        "beneficiaries": beneficiaries,
        "status_choices": Beneficiary.CURRENT_STATUS_CHOICES,
        "location_choices": Beneficiary.LOCATION_CHOICES,
        "sector_choices": Beneficiary._meta.get_field("skill_sector").choices,
        "gender_choices": Beneficiary.GENDER_CHOICES,
    }
    return render(request, "japa_development/beneficiary_list.html", context)

def beneficiary_detail(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    participations = beneficiary.pillar_participations.all()
    return render(request, "japa_development/beneficiary_detail.html", {"beneficiary": beneficiary, "participations": participations})

@require_http_methods(["GET"])
def api_dashboard_data(request):
    from django.db.models.functions import TruncMonth
    from datetime import datetime, timedelta

    location_data = list(Beneficiary.objects.filter(is_active=True).values("current_location_category").annotate(count=Count("id")).order_by("-count"))
    sector_data = list(Beneficiary.objects.filter(is_active=True).exclude(skill_sector="").values("skill_sector").annotate(count=Count("id")).order_by("-count"))
    twelve_months_ago = datetime.now() - timedelta(days=365)
    enrollment_trend = list(Beneficiary.objects.filter(enrolled_date__gte=twelve_months_ago).annotate(month=TruncMonth("enrolled_date")).values("month").annotate(count=Count("id")).order_by("month"))
    pillar_completion = []
    for pillar_code, pillar_name in PillarParticipation.PILLAR_CHOICES:
        total = PillarParticipation.objects.filter(pillar=pillar_code).count()
        completed = PillarParticipation.objects.filter(pillar=pillar_code, completed_date__isnull=False).count()
        pillar_completion.append({"pillar": pillar_name, "total": total, "completed": completed, "rate": round((completed/total*100),1) if total>0 else 0})

    return JsonResponse({
        "location_distribution": location_data,
        "sector_distribution": sector_data,
        "enrollment_trend": [{"month": item["month"].strftime("%Y-%m"), "count": item["count"]} for item in enrollment_trend],
        "pillar_completion": pillar_completion,
    })
