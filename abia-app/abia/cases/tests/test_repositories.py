import pytest
from abia.cases.repositories import CaseRepository

@pytest.mark.django_db
class TestCaseRepository:
    def test_count_returns_integer(self, db):
        result = CaseRepository.count()
        assert isinstance(result, int)

    def test_filter_count(self, db):
        result = CaseRepository.filter_count(status="open")
        assert isinstance(result, int)
        assert result >= 0
