"""Unified cross-app data access — Repository pattern."""
from django.db.models import Count
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.hotspot.models import HotspotPrediction


class UnifiedMetricsRepository:
    """Aggregates metrics across core apps for reporting layers."""

    @staticmethod
    def get_migrant_count():
        return Migrant.objects.count()

    @staticmethod
    def get_case_count():
        return Case.objects.count()

    @staticmethod
    def get_open_case_count():
        return Case.objects.filter(status="open").count()

    @staticmethod
    def get_resolved_case_count():
        return Case.objects.filter(status="resolved").count()

    @staticmethod
    def get_referral_count():
        return Referral.objects.count()

    @staticmethod
    def get_completed_referral_count():
        return Referral.objects.filter(status="completed").count()

    @staticmethod
    def get_returnee_count():
        return Migrant.objects.filter(status="returnee").count()

    @staticmethod
    def get_critical_cases():
        return Case.objects.filter(priority="critical").count()

    @staticmethod
    def get_protection_incidents():
        return Case.objects.filter(
            case_type__in=["trafficking", "gbv", "child_protection"]
        ).count()

    @staticmethod
    def get_resolved_protection_cases():
        return Case.objects.filter(
            case_type__in=["trafficking", "gbv", "child_protection"],
            status="resolved"
        ).count()

    @staticmethod
    def get_critical_hotspots():
        return HotspotPrediction.objects.filter(risk_level="critical").count()

    @staticmethod
    def get_lga_breakdown(limit=20):
        return list(Migrant.objects.values("current_lga__name").annotate(
            count=Count("id")
        ).order_by("-count")[:limit])

    @staticmethod
    def get_distinct_lga_count():
        return Migrant.objects.values("current_lga").distinct().count()

    @staticmethod
    def get_reintegration_count():
        return Migrant.objects.filter(status="reintegration").count()

    @staticmethod
    def get_skills_assessed_count():
        return Migrant.objects.filter(status="skills_assessed").count()