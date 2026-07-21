import pytest
from abia.migrants.repositories import MigrantRepository

@pytest.mark.django_db
class TestMigrantRepository:
    def test_count_returns_integer(self, db):
        result = MigrantRepository.count()
        assert isinstance(result, int)
        assert result >= 0

    def test_get_lga_breakdown_returns_list(self, db):
        result = MigrantRepository.get_lga_breakdown()
        assert isinstance(result, list)

    def test_get_distinct_lga_count_returns_integer(self, db):
        result = MigrantRepository.get_distinct_lga_count()
        assert isinstance(result, int)
        assert result >= 0

    def test_filter_count_with_no_matches(self, db):
        result = MigrantRepository.filter_count(status="nonexistent")
        assert result == 0
