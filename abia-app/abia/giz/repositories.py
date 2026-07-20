from .models import GIZDataExchange, GIZIndicator

class GIZDataExchangeRepository:
    @staticmethod
    def get_all():
        return GIZDataExchange.objects.all()

    @staticmethod
    def get_by_user(user):
        return GIZDataExchange.objects.filter(created_by=user)

    @staticmethod
    def get_by_id(exchange_id):
        return GIZDataExchange.objects.get(id=exchange_id)

    @staticmethod
    def update_status(exchange_id, status, submitted_at=None):
        exchange = GIZDataExchange.objects.get(id=exchange_id)
        exchange.status = status
        if submitted_at:
            exchange.submitted_at = submitted_at
        exchange.save()
        return exchange

class GIZIndicatorRepository:
    @staticmethod
    def get_active():
        return GIZIndicator.objects.filter(is_active=True)

    @staticmethod
    def update_current_value(name, value):
        GIZIndicator.objects.filter(name=name).update(current_value=value)