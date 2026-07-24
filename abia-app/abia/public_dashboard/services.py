"""Business logic layer for public dashboard. No ORM imports."""
from typing import Dict, Any
from datetime import datetime, timedelta
from .repositories import (
    MigrantRepository, CaseRepository, LGARepository, GeneratedReportRepository,
)


class DashboardService:
    @staticmethod
    def get_dashboard_context() -> Dict[str, Any]:
        total_migrants = MigrantRepository.get_total_count()
        total_cases = CaseRepository.get_total_count()
        resolved_cases = CaseRepository.get_resolved_count()
        active_cases = CaseRepository.get_active_count()
        six_months_ago = datetime.now() - timedelta(days=180)
        return {
            "total_migrants": total_migrants,
            "total_cases": total_cases,
            "resolved_cases": resolved_cases,
            "active_cases": active_cases,
            "resolution_rate": round(
                (resolved_cases / total_cases * 100), 1
            ) if total_cases else 0,
            "lga_data": list(LGARepository.get_all_with_migrant_counts()),
            "monthly_trend": MigrantRepository.get_monthly_trend(six_months_ago),
            "case_categories": CaseRepository.get_category_breakdown(),
            "recent_reports": list(GeneratedReportRepository.get_recent_public()),
            "last_updated": datetime.now(),
        }


class MapService:
    @staticmethod
    def get_geojson() -> Dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": LGARepository.get_map_features(),
        }