import pytest
from abia.hotspot.repositories import HotspotRepository

@pytest.mark.django_db
class TestHotspotRepository:
    def test_filter_count(self, db):
        result = HotspotRepository.filter_count(risk_level="critical")
        assert isinstance(result, int)
        assert result >= 0

    def test_filter_count_no_matches(self, db):
        result = HotspotRepository.filter_count(risk_level="nonexistent")
        assert result == 0
