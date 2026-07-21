import pytest
from decimal import Decimal
from abia.worldbank.models import WBIndicator, WBDataPoint
from abia.worldbank.repositories import WBIndicatorRepository

@pytest.mark.django_db
class TestWBIndicatorRepository:
    def test_get_active_returns_queryset(self, db):
        result = WBIndicatorRepository.get_active()
        assert result is not None

    def test_get_indicator_trend_with_no_data(self, db):
        result = WBIndicatorRepository.get_indicator_trend("FAKE.CODE")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_latest_for_indicator(self, db):
        ind = WBIndicator.objects.create(
            indicator_code="TEST.001",
            indicator_name="Test Indicator",
            category="test",
        )
        WBDataPoint.objects.create(
            indicator=ind, country_code="NGA", year=2026,
            value=Decimal("100.00"), country_name="Nigeria"
        )
        latest = WBIndicatorRepository.get_latest_for_indicator(ind)
        assert latest is not None
        assert latest.year == 2026

    def test_get_by_category_filters_correctly(self, db):
        WBIndicator.objects.create(
            indicator_code="MIG.001", indicator_name="Migration", category="migration"
        )
        result = WBIndicatorRepository.get_by_category("migration")
        assert result.count() >= 1
