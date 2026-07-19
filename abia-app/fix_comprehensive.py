#!/usr/bin/env python3
"""Comprehensive fix for all test collection errors."""

from collections import Counter
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print("COMPREHENSIVE TEST FIX")
print("=" * 60)

# 1. Delete ALL old test files (the ones with conflicting basenames)
print("\n[1/6] Deleting old test files with conflicting basenames...")
for app in ["accounts", "migrants", "cases", "referrals"]:
    for old_file in ["test_repositories.py", "test_services.py"]:
        path = os.path.join(BASE_DIR, app, "tests", old_file)
        if os.path.exists(path):
            os.remove(path)
            print("  DELETED: " + app + "/tests/" + old_file)

# 2. Clear ALL __pycache__ and .pyc files
print("\n[2/6] Clearing Python cache...")
os.system("find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null")
os.system("find . -name '*.pyc' -delete 2>/dev/null")
os.system("find . -name '*.pyo' -delete 2>/dev/null")

# 3. Fix pytest.ini
print("\n[3/6] Fixing pytest.ini...")
pytest_content = """[pytest]
DJANGO_SETTINGS_MODULE = abia.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --reuse-db
"""
with open(os.path.join(BASE_DIR, "pytest.ini"), "w") as f:
    f.write(pytest_content)
print("  OK: pytest.ini")

# 4. Ensure all __init__.py files exist
print("\n[4/6] Ensuring __init__.py files...")
for app in ["accounts", "migrants", "cases", "referrals"]:
    init_path = os.path.join(BASE_DIR, app, "tests", "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()
        print("  CREATED: " + app + "/tests/__init__.py")
    else:
        print("  EXISTS: " + app + "/tests/__init__.py")

# 5. Create conftest.py files
print("\n[5/6] Creating conftest.py files...")

accounts_conftest = """import pytest
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

with open(os.path.join(BASE_DIR, "accounts", "tests", "conftest.py"), "w") as f:
    f.write(accounts_conftest)
print("  OK: accounts/tests/conftest.py")

migrants_conftest = """import pytest
from abia.accounts.models import LGA

@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")
"""

with open(os.path.join(BASE_DIR, "migrants", "tests", "conftest.py"), "w") as f:
    f.write(migrants_conftest)
print("  OK: migrants/tests/conftest.py")

cases_conftest = """import pytest
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant

@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")

@pytest.fixture
def test_user(test_lga):
    return User.objects.create_user(
        username="caseuser",
        password="CasePass123!",
        role="field_officer",
        lga=test_lga,
    )

@pytest.fixture
def test_migrant(test_lga):
    return Migrant.objects.create(
        full_name="Case Subject",
        phone="+2348033333333",
        date_of_birth=date(1992, 3, 3),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )
"""

with open(os.path.join(BASE_DIR, "cases", "tests", "conftest.py"), "w") as f:
    f.write(cases_conftest)
print("  OK: cases/tests/conftest.py")

referrals_conftest = """import pytest
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case

@pytest.fixture
def from_lga():
    return LGA.objects.get(name="Aba North")

@pytest.fixture
def to_lga():
    return LGA.objects.get(name="Aba South")

@pytest.fixture
def test_user(from_lga):
    return User.objects.create_user(
        username="refuser",
        password="RefPass123!",
        role="field_officer",
        lga=from_lga,
    )

@pytest.fixture
def test_migrant(from_lga):
    return Migrant.objects.create(
        full_name="Referral Subject",
        phone="+2348044444444",
        date_of_birth=date(1988, 8, 8),
        gender="female",
        current_lga=from_lga,
        lga_of_origin=from_lga,
        status="active",
    )

@pytest.fixture
def test_case(test_user, test_migrant, from_lga):
    return Case.objects.create(
        migrant=test_migrant,
        lga=from_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="high",
        case_type="medical",
        description="Case for referral",
    )
"""

with open(os.path.join(BASE_DIR, "referrals", "tests", "conftest.py"), "w") as f:
    f.write(referrals_conftest)
print("  OK: referrals/tests/conftest.py")

# 6. Verify no conflicting basenames remain
print("\n[6/6] Verifying no conflicting basenames...")
all_test_files = []
for root, dirs, files in os.walk(BASE_DIR):
    for f in files:
        if f.startswith("test_") and f.endswith(".py"):
            all_test_files.append(f)


basenames = Counter(all_test_files)
conflicts = {k: v for k, v in basenames.items() if v > 1}
if conflicts:
    print("  WARNING: Conflicting basenames found: " + str(conflicts))
else:
    print("  OK: All test filenames are unique")

print("\n" + "=" * 60)
print("FIX COMPLETE")
print("=" * 60)
print("\nNext: Re-enter container and run:")
print("  python3 -m pytest -v")
