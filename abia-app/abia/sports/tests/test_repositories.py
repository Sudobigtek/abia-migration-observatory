import pytest
from decimal import Decimal
from datetime import date
from abia.sports.models import AthleteProfile, AthleteTransfer
from abia.sports.repositories import AthleteRepository, TransferRepository

@pytest.mark.django_db
class TestAthleteRepository:
    def test_get_active_returns_queryset(self, db):
        result = AthleteRepository.get_active()
        assert result is not None

    def test_get_by_sport_returns_list(self, db):
        result = AthleteRepository.get_by_sport()
        assert isinstance(result, list)

    def test_get_top_valued_respects_limit(self, db):
        result = AthleteRepository.get_top_valued(5)
        assert isinstance(result, list)
        assert len(result) <= 5

    def test_get_lga_talent_map_returns_list(self, db):
        result = AthleteRepository.get_lga_talent_map()
        assert isinstance(result, list)

@pytest.mark.django_db
class TestTransferRepository:
    def test_get_talent_export_value_empty(self, db):
        result = TransferRepository.get_talent_export_value()
        assert isinstance(result, dict)
        assert "total_transfer_value_usd" in result
        assert "international_transfers" in result

    def test_get_talent_export_value_with_data(self, db):
        athlete = AthleteProfile.objects.create(
            full_name="Test Player", sport="football", is_active=True
        )
        AthleteTransfer.objects.create(
            athlete=athlete, from_club="Local FC", from_country="Nigeria",
            to_club="Foreign FC", to_country="England",
            transfer_fee_usd=Decimal("500000.00"), transfer_date=date(2026, 6, 1),
            is_international=True, status="completed"
        )
        result = TransferRepository.get_talent_export_value()
        assert result["international_transfers"] >= 1
        assert result["total_transfer_value_usd"] >= 500000

    def test_get_by_destination_returns_list(self, db):
        result = TransferRepository.get_by_destination()
        assert isinstance(result, list)
