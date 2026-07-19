import re

from abia.migrants.repositories import MigrantRepository
from common.exceptions import (
    DuplicateMigrantError,
    InvalidPhoneError,
    LGAAccessDenied,
    MigrantNotFoundError,
)

PHONE_REGEX = re.compile(r"^\+\d{10,15}$")


class MigrantService:
    @staticmethod
    def _get_lga_id(lga_obj):
        return lga_obj.id if hasattr(lga_obj, "id") else lga_obj

    @staticmethod
    def get_by_id(migrant_id):
        migrant = MigrantRepository.get_by_id(migrant_id)
        if not migrant:
            raise MigrantNotFoundError("Migrant not found")
        return migrant

    @staticmethod
    def get_migrants_for_request(request):
        user = request.user
        if user.role in ("state_admin", "super_admin"):
            return MigrantRepository.get_all()
        return MigrantRepository.get_by_lga(user.lga.id)

    @staticmethod
    def create_migrant(data, officer):
        if officer.role == "field_officer":
            data_lga_id = MigrantService._get_lga_id(data.get("current_lga"))
            officer_lga_id = MigrantService._get_lga_id(officer.lga)
            if data_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot create migrant outside your LGA")
        phone = data.get("phone", "")
        if not PHONE_REGEX.match(phone):
            raise InvalidPhoneError("Invalid phone number format")
        lga_migrants = MigrantRepository.get_by_lga(officer.lga.id)
        for m in lga_migrants:
            if m.phone == phone:
                raise DuplicateMigrantError("Phone number already registered")
        data["created_by"] = officer
        return MigrantRepository.create(data)

    @staticmethod
    def update_migrant(migrant_id, data, officer):
        migrant = MigrantRepository.get_by_id(migrant_id)
        if not migrant:
            raise MigrantNotFoundError("Migrant not found")
        if officer.role == "field_officer":
            migrant_lga_id = MigrantService._get_lga_id(migrant.current_lga)
            officer_lga_id = MigrantService._get_lga_id(officer.lga)
            if migrant_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot update migrant outside your LGA")
        return MigrantRepository.update(migrant_id, data)

    @staticmethod
    def delete_migrant(migrant_id, officer):
        migrant = MigrantRepository.get_by_id(migrant_id)
        if not migrant:
            raise MigrantNotFoundError("Migrant not found")
        if officer.role == "field_officer":
            migrant_lga_id = MigrantService._get_lga_id(migrant.current_lga)
            officer_lga_id = MigrantService._get_lga_id(officer.lga)
            if migrant_lga_id != officer_lga_id:
                raise LGAAccessDenied("Cannot delete migrant outside your LGA")
        return MigrantRepository.delete(migrant_id)
