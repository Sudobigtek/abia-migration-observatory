from .repositories import RemittanceRepository

class CBNService:
    @staticmethod
    def get_summary():
        return RemittanceRepository.get_summary()

    @staticmethod
    def get_by_lga():
        return RemittanceRepository.get_by_lga()

    @staticmethod
    def get_by_channel():
        return RemittanceRepository.get_by_channel()

    @staticmethod
    def get_by_purpose():
        return RemittanceRepository.get_by_purpose()

    @staticmethod
    def get_monthly_trends():
        return RemittanceRepository.get_monthly_trends()