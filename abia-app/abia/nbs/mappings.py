"""State schema → NBS schema field mappings."""
from typing import Dict


NBS_MIGRATION_MAPPING: Dict[str, str] = {
    "full_name": "name_of_migrant",
    "date_of_birth": "date_of_birth",
    "current_lga": "lga_of_residence",
    "country_of_destination": "destination_country",
    "occupation": "isco_code",
    "date_of_departure": "departure_date",
}
