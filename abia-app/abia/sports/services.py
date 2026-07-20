from .repositories import AthleteRepository, TransferRepository

class SportsService:
    @staticmethod
    def get_transfers_by_destination():
        return TransferRepository.get_by_destination()

    @staticmethod
    def get_talent_export_value():
        return TransferRepository.get_talent_export_value()

    @staticmethod
    def get_by_sport():
        return AthleteRepository.get_by_sport()

    @staticmethod
    def get_top_valued_athletes(limit=20):
        return AthleteRepository.get_top_valued(limit)

    @staticmethod
    def get_lga_talent_map():
        return AthleteRepository.get_lga_talent_map()