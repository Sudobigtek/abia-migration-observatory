from django.db.models import Count, Sum
from .repositories import GIZDataExchangeRepository, GIZIndicatorRepository
from abia.migrants.repositories import MigrantRepository
from abia.cases.repositories import CaseRepository
from abia.referrals.repositories import ReferralRepository

class GIZService:
    @staticmethod
    def build_migration_governance_report():
        return {
            "programme_area": "migration_governance",
            "reporting_period": "Q3-2026",
            "indicators": {
                "migrants_registered": MigrantRepository.count(),
                "cases_managed": CaseRepository.count(),
                "referrals_completed": ReferralRepository.filter_count(status="completed"),
                "lgas_covered": MigrantRepository.get_distinct_lga_count(),
                "data_quality_score": 95.0,
            },
            "breakdown_by_lga": MigrantRepository.get_lga_breakdown(20),
        }

    @staticmethod
    def build_reintegration_report():
        return {
            "programme_area": "reintegration",
            "reporting_period": "Q3-2026",
            "indicators": {
                "returnees_registered": MigrantRepository.filter_count(status="returnee"),
                "reintegration_plans_developed": MigrantRepository.filter_count(status="reintegration"),
                "skills_assessed": MigrantRepository.filter_count(status="skills_assessed"),
            },
        }

    @staticmethod
    def build_protection_report():
        return {
            "programme_area": "protection_assistance",
            "reporting_period": "Q3-2026",
            "indicators": {
                "protection_cases": CaseRepository.filter_count(case_type__in=["trafficking", "gbv", "child_protection"]),
                "cases_resolved": CaseRepository.filter_count(case_type__in=["trafficking", "gbv", "child_protection"], status="resolved"),
                "referrals_to_shelter": 0,
            },
        }

    @staticmethod
    def update_indicators_from_data():
        indicators = {
            "migrants_registered": MigrantRepository.count(),
            "cases_managed": CaseRepository.count(),
            "referrals_completed": ReferralRepository.filter_count(status="completed"),
            "returnees_registered": MigrantRepository.filter_count(status="returnee"),
        }
        for name, value in indicators.items():
            GIZIndicatorRepository.update_current_value(name, value)
        return indicators

    @staticmethod
    def submit_to_giz(exchange_id):
        from django.utils import timezone
        return GIZDataExchangeRepository.update_status(exchange_id, "submitted", timezone.now())