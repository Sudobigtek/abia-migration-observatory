from .repositories import ECOWASMigrantFlowRepository, ECOWASTradeFlowRepository

class ECOWASService:
    @staticmethod
    def get_migration_by_corridor():
        return ECOWASMigrantFlowRepository.get_migration_by_corridor()

    @staticmethod
    def get_migration_by_sector(year=None):
        return ECOWASMigrantFlowRepository.get_migration_by_sector(year)

    @staticmethod
    def get_free_movement_stats(year=None):
        return ECOWASMigrantFlowRepository.get_free_movement_stats(year)

    @staticmethod
    def get_intra_regional_trade(year=None):
        return ECOWASTradeFlowRepository.get_intra_regional_trade(year)