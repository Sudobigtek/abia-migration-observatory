import pytest
from abia.ecowas.models import ECOWASMigrantFlow, ECOWASTradeFlow
from abia.ecowas.repositories import ECOWASMigrantFlowRepository, ECOWASTradeFlowRepository

@pytest.mark.django_db
class TestECOWASMigrantFlowRepository:
    def test_get_migration_by_corridor_empty(self, db):
        result = ECOWASMigrantFlowRepository.get_migration_by_corridor()
        assert isinstance(result, list)

    def test_get_migration_by_corridor_with_data(self, db):
        ECOWASMigrantFlow.objects.create(
            country_of_origin="Nigeria", country_of_destination="Ghana",
            migration_type="labour", estimated_count=5000, year=2026
        )
        result = ECOWASMigrantFlowRepository.get_migration_by_corridor()
        assert len(result) >= 1
        assert result[0]["country_of_origin"] == "Nigeria"

    def test_get_free_movement_stats(self, db):
        ECOWASMigrantFlow.objects.create(
            country_of_origin="Nigeria", country_of_destination="Ghana",
            migration_type="labour", gender="male", estimated_count=3000, year=2026
        )
        result = ECOWASMigrantFlowRepository.get_free_movement_stats(2026)
        assert "total_labour_migrants" in result
        assert result["total_labour_migrants"] == 3000

@pytest.mark.django_db
class TestECOWASTradeFlowRepository:
    def test_get_intra_regional_trade(self, db):
        ECOWASTradeFlow.objects.create(
            reporter_country="Nigeria", partner_country="Ghana",
            export_value=100000, import_value=50000, year=2026
        )
        result = ECOWASTradeFlowRepository.get_intra_regional_trade(2026)
        assert result["total_exports"] >= 100000
        assert len(result["top_partners"]) >= 1
