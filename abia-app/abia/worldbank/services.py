from .repositories import WBIndicatorRepository

class WorldBankService:
    @staticmethod
    def get_indicator_trend(indicator_code, country_code="NGA"):
        return WBIndicatorRepository.get_indicator_trend(indicator_code, country_code)

    @staticmethod
    def get_latest_values(category=None):
        results = []
        for ind in WBIndicatorRepository.get_by_category(category):
            latest = WBIndicatorRepository.get_latest_for_indicator(ind)
            if latest:
                results.append({
                    "indicator_code": ind.indicator_code,
                    "indicator_name": ind.indicator_name,
                    "year": latest.year,
                    "value": latest.value,
                    "unit": ind.unit,
                })
        return results

    @staticmethod
    def get_migration_indicators():
        return WorldBankService.get_latest_values(category="migration")

    @staticmethod
    def get_remittance_indicators():
        return WorldBankService.get_latest_values(category="remittance")
