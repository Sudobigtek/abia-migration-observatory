from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.hotspot.models import HotspotPrediction
from abia.ncfrmi_reporting.models import NCFRMIMonthlyReport
from abia.iom.models import IOMDataExchange


@login_required
def dashboard_stats_api(request):
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    months = []
    migrant_counts = []
    case_counts = []
    for i in range(5, -1, -1):
        m = ((now.month - 1 - i) % 12) + 1
        y = now.year + ((now.month - 1 - i) // 12)
        months.append(f"{y}-{m:02d}")
        migrant_counts.append(Migrant.objects.filter(created_at__year=y, created_at__month=m).count())
        case_counts.append(Case.objects.filter(created_at__year=y, created_at__month=m).count())

    case_status = Case.objects.values("status").annotate(count=Count("id")).order_by("status")
    referral_status = Referral.objects.values("status").annotate(count=Count("id")).order_by("status")
    case_priority = Case.objects.values("priority").annotate(count=Count("id")).order_by("priority")
    lga_vulnerability = Migrant.objects.values("current_lga__name").annotate(
        count=Count("id"),
        vulnerable=Count("id", filter=Q(is_vulnerable=True))
    ).order_by("-count")[:10]
    hotspot_severity = HotspotPrediction.objects.values("risk_level").annotate(count=Count("id")).order_by("risk_level")

    summary = {
        "total_migrants": Migrant.objects.count(),
        "total_cases": Case.objects.count(),
        "open_cases": Case.objects.filter(status="open").count(),
        "pending_referrals": Referral.objects.filter(status="pending").count(),
        "active_hotspots": HotspotPrediction.objects.filter(risk_level__in=["high", "critical"]).count(),
        "ncfrmi_reports": NCFRMIMonthlyReport.objects.count(),
        "iom_reports": IOMDataExchange.objects.count(),
        "this_month_migrants": Migrant.objects.filter(created_at__year=current_year, created_at__month=current_month).count(),
        "this_month_cases": Case.objects.filter(created_at__year=current_year, created_at__month=current_month).count(),
    }

    return JsonResponse({
        "months": months,
        "migrant_counts": migrant_counts,
        "case_counts": case_counts,
        "case_status": list(case_status),
        "referral_status": list(referral_status),
        "case_priority": list(case_priority),
        "lga_vulnerability": list(lga_vulnerability),
        "hotspot_severity": list(hotspot_severity),
        "summary": summary,
    })


@login_required
def hotspot_geojson_api(request):
    """GeoJSON API for Leaflet map — all high/critical hotspot predictions."""
    alerts = HotspotPrediction.objects.filter(risk_level__in=["high", "critical"]).select_related("lga")
    features = []
    for alert in alerts:
        # Extract lat/lng from PostGIS PointField
        lat = alert.centroid.y if alert.centroid else 5.45
        lng = alert.centroid.x if alert.centroid else 7.5
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lng), float(lat)]
            },
            "properties": {
                "id": str(alert.id),
                "title": f"{alert.lga.name if alert.lga else 'Unknown'} Hotspot",
                "description": f"Risk score: {alert.risk_score}. Factors: {alert.contributing_factors}",
                "severity": alert.risk_level,
                "lga": alert.lga.name if alert.lga else "Unknown",
                "created_at": alert.created_at.isoformat(),
                "affected_count": alert.predicted_migrant_count or 0,
            }
        })
    return JsonResponse({"type": "FeatureCollection", "features": features})
