import pytest
from decimal import Decimal
from abia.wto.models import TradeRecord
from abia.wto.repositories import TradeRecordRepository

@pytest.mark.django_db
class TestTradeRecordRepository:
    def test_get_trade_balance_by_sector_empty(self, db):
        result = TradeRecordRepository.get_trade_balance_by_sector()
        assert isinstance(result, list)

    def test_get_trade_balance_with_data(self, db):
        TradeRecord.objects.create(
            flow_type="export", product_category="Cocoa", sector="agriculture",
            value_usd=Decimal("50000.00"), trade_partner="Ghana", year=2026
        )
        TradeRecord.objects.create(
            flow_type="import", product_category="Machinery", sector="manufacturing",
            value_usd=Decimal("30000.00"), trade_partner="China", year=2026
        )
        result = TradeRecordRepository.get_trade_balance_by_sector(2026)
        sectors = [r["sector"] for r in result]
        assert "agriculture" in sectors
        assert "manufacturing" in sectors

    def test_get_top_partners_limits_results(self, db):
        result = TradeRecordRepository.get_top_partners(limit=5)
        assert isinstance(result, list)
        assert len(result) <= 5

    def test_get_yearly_summary_returns_list(self, db):
        result = TradeRecordRepository.get_yearly_summary()
        assert isinstance(result, list)
