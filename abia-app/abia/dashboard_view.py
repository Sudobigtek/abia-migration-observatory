from django.shortcuts import render
from abia.charts.services import ChartService

def unified_dashboard(request):
    context = {
        "summary": ChartService.get_unified_summary(),
        "remittances_by_lga": ChartService.get_remittances_by_lga(),
        "remittances_by_channel": ChartService.get_remittances_by_channel(),
        "trade_balance": ChartService.get_trade_balance(),
        "labour_trade": ChartService.get_labour_intensive_trade(),
        "ecowas_corridors": ChartService.get_ecowas_corridors(),
        "sports_destinations": ChartService.get_sports_by_destination(),
        "sports_lga": ChartService.get_sports_lga_map(),
        "migrants_by_lga": ChartService.get_migrants_by_lga(),
    }
    return render(request, "dashboard.html", context)
