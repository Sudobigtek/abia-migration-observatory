import pytest
from decimal import Decimal
from datetime import datetime
from abia.cbn.models import RemittanceRecord
from abia.cbn.repositories import RemittanceRepository

@pytest.mark.django_db
class TestRemittanceRepository:
    def test_get_summary_returns_dict_with_keys(self, db):
        result = RemittanceRepository.get_summary()
        assert isinstance(result, dict)
        assert "total_naira" in result
        assert "total_count" in result
        assert "avg_amount" in result

    def test_get_by_lga_returns_list(self, db):
        result = RemittanceRepository.get_by_lga()
        assert isinstance(result, list)

    def test_get_by_channel_returns_list(self, db):
        result = RemittanceRepository.get_by_channel()
        assert isinstance(result, list)

    def test_get_monthly_trends_returns_list(self, db):
        result = RemittanceRepository.get_monthly_trends()
        assert isinstance(result, list)

    def test_created_record_appears_in_summary(self, db):
        RemittanceRecord.objects.create(
            sender_name="Test Sender",
            amount_sent=Decimal("1000.00"),
            naira_equivalent=Decimal("1550000.00"),
            recipient_name="Test Recipient",
            transaction_reference="TXN-TEST-001",
            transaction_date=datetime.now(),
            status="completed",
        )
        result = RemittanceRepository.get_summary()
        assert result["total_count"] >= 1
