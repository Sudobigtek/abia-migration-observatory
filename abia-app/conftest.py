import pytest

from abia.accounts.models import LGA, User

LGA_SEED_DATA = [
    {"name": "Aba North", "code": "ABN", "population_2023": 154000},
    {"name": "Aba South", "code": "ABS", "population_2023": 142000},
    {"name": "Arochukwu", "code": "ARO", "population_2023": 89000},
    {"name": "Bende", "code": "BEN", "population_2023": 78000},
    {"name": "Ikwuano", "code": "IKW", "population_2023": 65000},
    {"name": "Isiala Ngwa North", "code": "INN", "population_2023": 112000},
    {"name": "Isiala Ngwa South", "code": "INS", "population_2023": 98000},
    {"name": "Isuikwuato", "code": "ISU", "population_2023": 72000},
    {"name": "Obi Ngwa", "code": "OBN", "population_2023": 135000},
    {"name": "Ohafia", "code": "OHA", "population_2023": 105000},
    {"name": "Osisioma", "code": "OSI", "population_2023": 128000},
    {"name": "Ugwunagbo", "code": "UGW", "population_2023": 87000},
    {"name": "Ukwa East", "code": "UKE", "population_2023": 69000},
    {"name": "Ukwa West", "code": "UKW", "population_2023": 74000},
    {"name": "Umuahia North", "code": "UMN", "population_2023": 198000},
    {"name": "Umuahia South", "code": "UMS", "population_2023": 156000},
    {"name": "Umunneochi", "code": "UMU", "population_2023": 82000},
]


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        for data in LGA_SEED_DATA:
            LGA.objects.get_or_create(code=data["code"], defaults=data)
        lga = LGA.objects.first()
        if lga:
            User.objects.create_user(
                username="testuser",
                password="TestPass123",
                role="field_officer",
                lga=lga,
            )


@pytest.fixture
def test_user(db):
    return User.objects.get(username="testuser")
