import pytest
from abia.giz.models import GIZDataExchange, GIZIndicator
from abia.giz.repositories import GIZDataExchangeRepository, GIZIndicatorRepository

@pytest.mark.django_db
class TestGIZDataExchangeRepository:
    def test_get_all_returns_queryset(self, db):
        result = GIZDataExchangeRepository.get_all()
        assert result is not None

    def test_get_by_user_filters_correctly(self, db, admin_user):
        GIZDataExchange.objects.create(
            programme_area="migration_governance", title="Test Exchange",
            description="Test", created_by=admin_user
        )
        result = GIZDataExchangeRepository.get_by_user(admin_user)
        assert result.count() >= 1

    def test_update_status_changes_state(self, db, admin_user):
        exchange = GIZDataExchange.objects.create(
            programme_area="migration_governance", title="Test",
            description="Test", created_by=admin_user
        )
        updated = GIZDataExchangeRepository.update_status(exchange.id, "submitted")
        assert updated.status == "submitted"

@pytest.mark.django_db
class TestGIZIndicatorRepository:
    def test_get_active_returns_queryset(self, db):
        result = GIZIndicatorRepository.get_active()
        assert result is not None

    def test_update_current_value(self, db):
        GIZIndicator.objects.create(name="test_indicator", target_value=100)
        GIZIndicatorRepository.update_current_value("test_indicator", 75)
        ind = GIZIndicator.objects.get(name="test_indicator")
        assert ind.current_value == 75
