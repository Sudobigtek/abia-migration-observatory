"""Migrants business logic layer."""
from .repositories import MigrantRepository
from .exceptions import LGAAccessDenied, MigrantNotFoundError, DuplicateSubmissionError

class MigrantService:
    @staticmethod
    def get_migrants_for_request(request):
        user = request.user
        if user.role in ("state_admin", "super_admin"):
            return MigrantRepository.get_all()
        return MigrantRepository.get_by_lga(user.lga_id)

    @staticmethod
    def create_migrant(data, creator):
        if creator.role == "field_officer" and data.get("current_lga") != creator.lga:
            raise LGAAccessDenied("Cannot register migrant outside your LGA")
        odk_id = data.get("odk_submission_id")
        if odk_id and MigrantRepository.exists_by_odk_id(odk_id):
            raise DuplicateSubmissionError()
        return MigrantRepository.create(data)

    @staticmethod
    def get_migrant_by_id(migrant_id, requester):
        migrant = MigrantRepository.get_by_id(migrant_id)
        if not migrant:
            raise MigrantNotFoundError()
        if requester.role not in ("state_admin", "super_admin"):
            if migrant.current_lga != requester.lga:
                raise LGAAccessDenied()
        return migrant

    @staticmethod
    def update_migrant(migrant_id, data, requester):
        MigrantService.get_migrant_by_id(migrant_id, requester)
        return MigrantRepository.update(migrant_id, data)

    @staticmethod
    def delete_migrant(migrant_id, requester):
        MigrantService.get_migrant_by_id(migrant_id, requester)
        MigrantRepository.delete(migrant_id)
