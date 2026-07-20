from django.db.models import Count, Sum
from .models import GIZDataExchange, GIZIndicator

class GIZService:
    @staticmethod
    def build_migration_governance_report():
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        from abia.referrals.models import Referral
        return {
            "programme_area": "migration_governance",
            "reporting_period": "Q3-2026",
            "indicators": {
                "migrants_registered": Migrant.objects.count(),
                "cases_managed": Case.objects.count(),
                "referrals_completed": Referral.objects.filter(status="completed").count(),
                "lgas_covered": Migrant.objects.values("current_lga").distinct().count(),
                "data_quality_score": 95.0,
            },
            "breakdown_by_lga": list(Migrant.objects.values("current_lga__name").annotate(
                count=Count("id")).values("current_lga__name", "count")[:20]),
        }

    @staticmethod
    def build_reintegration_report():
        from abia.migrants.models import Migrant
        return {
            "programme_area": "reintegration",
            "reporting_period": "Q3-2026",
            "indicators": {
                "returnees_registered": Migrant.objects.filter(status="returnee").count(),
                "reintegration_plans_developed": Migrant.objects.filter(status="reintegration").count(),
                "skills_assessed": Migrant.objects.filter(status="skills_assessed").count(),
            },
        }

    @staticmethod
    def build_protection_report():
        from abia.cases.models import Case
        return {
            "programme_area": "protection_assistance",
            "reporting_period": "Q3-2026",
            "indicators": {
                "protection_cases": Case.objects.filter(case_type__in=["trafficking", "gbv", "child_protection"]).count(),
                "cases_resolved": Case.objects.filter(case_type__in=["trafficking", "gbv", "child_protection"], status="resolved").count(),
                "referrals_to_shelter": 0,
            },
        }

    @staticmethod
    def update_indicators_from_data():
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        from abia.referrals.models import Referral
        indicators = {
            "migrants_registered": Migrant.objects.count(),
            "cases_managed": Case.objects.count(),
            "referrals_completed": Referral.objects.filter(status="completed").count(),
            "returnees_registered": Migrant.objects.filter(status="returnee").count(),
        }
        for name, value in indicators.items():
            GIZIndicator.objects.filter(name=name).update(current_value=value)
        return indicators

    @staticmethod
    def submit_to_giz(exchange_id):
        from django.utils import timezone
        exchange = GIZDataExchange.objects.get(id=exchange_id)
        exchange.status = "submitted"
        exchange.submitted_at = timezone.now()
        exchange.save()
        return exchange