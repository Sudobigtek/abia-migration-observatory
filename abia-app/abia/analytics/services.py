from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def get_migration_overview():
    cache_key = "analytics:migration_overview"
    cached = cache.get(cache_key)
    if cached:
        return cached
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.referrals.models import Referral
    total_migrants = Migrant.objects.count()
    active_migrants = Migrant.objects.filter(status="active").count()
    total_cases = Case.objects.count()
    open_cases = Case.objects.filter(status__in=["open", "in_progress"]).count()
    total_referrals = Referral.objects.count()
    pending_referrals = Referral.objects.filter(status="pending").count()
    result = {
        "total_migrants": total_migrants,
        "active_migrants": active_migrants,
        "total_cases": total_cases,
        "open_cases": open_cases,
        "resolved_cases": total_cases - open_cases,
        "total_referrals": total_referrals,
        "pending_referrals": pending_referrals,
        "timestamp": timezone.now().isoformat(),
    }
    cache.set(cache_key, result, timeout=300)
    return result

def get_cases_by_lga():
    cache_key = "analytics:cases_by_lga"
    cached = cache.get(cache_key)
    if cached:
        return cached
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT g.name, COUNT(c.id) as case_count
            FROM cases_case c
            LEFT JOIN geo_lga g ON c.lga_id = g.id
            GROUP BY g.name
            ORDER BY case_count DESC
        """)
        rows = cursor.fetchall()
    result = [{"lga": row[0] or "Unknown", "cases": row[1]} for row in rows]
    cache.set(cache_key, result, timeout=300)
    return result

def get_cases_by_type():
    cache_key = "analytics:cases_by_type"
    cached = cache.get(cache_key)
    if cached:
        return cached
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT case_type, COUNT(id) as count,
                   SUM(CASE WHEN status IN ("open", "in_progress") THEN 1 ELSE 0 END) as open_count
            FROM cases_case
            GROUP BY case_type
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
    result = [{"type": row[0], "total": row[1], "open": row[2]} for row in rows]
    cache.set(cache_key, result, timeout=300)
    return result

def get_monthly_trends(months=12):
    cache_key = f"analytics:monthly_trends:{months}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30*months)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE_TRUNC("month", created_at) as month,
                   COUNT(id) as count
            FROM migrants_migrant
            WHERE created_at >= %s
            GROUP BY month
            ORDER BY month
        """, [start_date])
        migrant_rows = cursor.fetchall()
        cursor.execute("""
            SELECT DATE_TRUNC("month", created_at) as month,
                   COUNT(id) as count
            FROM cases_case
            WHERE created_at >= %s
            GROUP BY month
            ORDER BY month
        """, [start_date])
        case_rows = cursor.fetchall()
    result = {
        "migrants_by_month": [{"month": str(row[0])[:7], "count": row[1]} for row in migrant_rows],
        "cases_by_month": [{"month": str(row[0])[:7], "count": row[1]} for row in case_rows],
        "period_months": months,
    }
    cache.set(cache_key, result, timeout=300)
    return result

def get_risk_distribution():
    cache_key = "analytics:risk_distribution"
    cached = cache.get(cache_key)
    if cached:
        return cached
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT risk_level, COUNT(id) as count,
                   AVG(risk_score) as avg_score
            FROM ai_riskassessment
            GROUP BY risk_level
        """)
        rows = cursor.fetchall()
    result = [{"level": row[0], "count": row[1], "avg_score": round(row[2] or 0, 2)} for row in rows]
    cache.set(cache_key, result, timeout=300)
    return result

def get_recent_activity(limit=20):
    from abia.migrants.models import Migrant
    from abia.cases.models import Case
    from abia.ai.models import RiskAssessment
    recent_migrants = list(Migrant.objects.order_by("-created_at")[:limit].values("id", "full_name", "created_at"))
    recent_cases = list(Case.objects.order_by("-created_at")[:limit].values("id", "case_type", "status", "created_at"))
    recent_assessments = list(RiskAssessment.objects.order_by("-created_at")[:limit].values("id", "risk_level", "risk_score", "created_at"))
    return {
        "migrants": [{"id": str(m["id"]), "name": m["full_name"], "time": m["created_at"].isoformat() if m["created_at"] else None} for m in recent_migrants],
        "cases": [{"id": str(c["id"]), "type": c["case_type"], "status": c["status"], "time": c["created_at"].isoformat() if c["created_at"] else None} for c in recent_cases],
        "assessments": [{"id": str(a["id"]), "level": a["risk_level"], "score": a["risk_score"], "time": a["created_at"].isoformat() if a["created_at"] else None} for a in recent_assessments],
    }
