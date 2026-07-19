#!/usr/bin/env python3
import os

# Fix 1: Create conftest.py with LGA + User seed data
conftest_content = """import pytest
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

@pytest.fixture(scope="session", autouse=True)
def seed_lgas(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        if LGA.objects.count() == 0:
            for data in LGA_SEED_DATA:
                LGA.objects.get_or_create(code=data["code"], defaults=data)

@pytest.fixture(scope="session", autouse=True)
def seed_users(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        if User.objects.count() == 0:
            lga = LGA.objects.first()
            if lga:
                User.objects.create_user(
                    username="testuser",
                    password="TestPass123!",
                    role="field_officer",
                    lga=lga,
                )
"""

with open("accounts/tests/conftest.py", "w") as f:
    f.write(conftest_content)
print("OK: accounts/tests/conftest.py")

# Fix 2: Correct pytest.ini
pytest_content = """[pytest]
DJANGO_SETTINGS_MODULE = abia.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --reuse-db
"""

with open("pytest.ini", "w") as f:
    f.write(pytest_content)
print("OK: pytest.ini")

print(
    "All fixes applied. Run: python3 -m pytest accounts/tests/test_accounts_repositories.py -v"
)
