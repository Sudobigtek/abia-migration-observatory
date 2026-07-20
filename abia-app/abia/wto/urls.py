from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TradeRecordViewSet, WTOConfigurationViewSet, trade_balance, top_partners, labour_intensive_trade, yearly_summary

router = DefaultRouter()
router.register(r"records", TradeRecordViewSet, basename="traderecord")
router.register(r"config", WTOConfigurationViewSet, basename="wtoconfig")

urlpatterns = [
    path("", include(router.urls)),
    path("balance/", trade_balance, name="wto-balance"),
    path("top-partners/", top_partners, name="wto-top-partners"),
    path("labour-intensive/", labour_intensive_trade, name="wto-labour"),
    path("yearly-summary/", yearly_summary, name="wto-yearly"),
]