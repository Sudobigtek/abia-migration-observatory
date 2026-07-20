from .repositories import TradeRecordRepository

class WTOService:
    @staticmethod
    def get_trade_balance_by_sector(year=None):
        return TradeRecordRepository.get_trade_balance_by_sector(year)

    @staticmethod
    def get_top_partners(flow_type="export", year=None, limit=10):
        return TradeRecordRepository.get_top_partners(flow_type, year, limit)

    @staticmethod
    def get_labour_intensive_trade(year=None):
        return TradeRecordRepository.get_labour_intensive_trade(year)

    @staticmethod
    def get_yearly_summary():
        return TradeRecordRepository.get_yearly_summary()