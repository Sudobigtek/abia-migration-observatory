import pytest
from abia.referrals.repositories import ReferralRepository

@pytest.mark.django_db
class TestReferralRepository:
    def test_count_returns_integer(self, db):
        result = ReferralRepository.count()
        assert isinstance(result, int)

    def test_filter_count(self, db):
        result = ReferralRepository.filter_count(status="pending")
        assert isinstance(result, int)
        assert result >= 0
