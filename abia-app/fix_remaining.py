import os, re

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# =====================================================================
# Fix tenant/views.py
# =====================================================================
t = "abia/tenant/views.py"
if os.path.exists(t):
    c = read(t)
    if "extend_schema" not in c:
        c = 'from drf_spectacular.utils import extend_schema, inline_serializer\nfrom rest_framework import serializers\n\n' + c
    if "def my_permissions" in c and "@extend_schema" not in c.split("def my_permissions")[0].split("\ndef ")[-1]:
        c = c.replace(
            "def my_permissions(request):",
            '@extend_schema(\n    responses=inline_serializer("MyPermissionsResponse", fields={"permissions": serializers.ListField(child=serializers.CharField())}),\n    tags=["Tenant"],\n    summary="Get my permissions",\n)\ndef my_permissions(request):'
        )
        write(t, c)

# =====================================================================
# Fix throttle/views.py
# =====================================================================
th = "abia/throttle/views.py"
if os.path.exists(th):
    c = read(th)
    if "extend_schema" not in c:
        c = 'from drf_spectacular.utils import extend_schema, inline_serializer\nfrom rest_framework import serializers\n\n' + c
    if "def my_rate_limit" in c:
        c = c.replace(
            "def my_rate_limit(request):",
            '@extend_schema(\n    responses=inline_serializer("RateLimitResponse", fields={"limit": serializers.IntegerField(), "remaining": serializers.IntegerField()}),\n    tags=["System"],\n    summary="Get my rate limit",\n)\ndef my_rate_limit(request):'
        )
    if "def throttle_stats" in c:
        c = c.replace(
            "def throttle_stats(request):",
            '@extend_schema(\n    responses=inline_serializer("ThrottleStatsResponse", fields={"total_requests": serializers.IntegerField(), "throttled": serializers.IntegerField()}),\n    tags=["System"],\n    summary="Throttle statistics",\n)\ndef throttle_stats(request):'
        )
    write(th, c)

# =====================================================================
# Fix webhooks/views.py - retry_failed and trigger_event
# =====================================================================
wh = "abia/webhooks/views.py"
if os.path.exists(wh):
    c = read(wh)
    # Check if these are functions or methods
    if "def retry_failed(request):" in c:
        c = c.replace(
            "def retry_failed(request):",
            '@extend_schema(\n    responses=inline_serializer("RetryFailedResponse", fields={"retried": serializers.IntegerField(), "failed_ids": serializers.ListField(child=serializers.CharField())}),\n    tags=["Webhooks"],\n    summary="Retry failed webhook deliveries",\n)\ndef retry_failed(request):'
        )
    if "def trigger_event(request):" in c:
        c = c.replace(
            "def trigger_event(request):",
            '@extend_schema(\n    responses=inline_serializer("TriggerEventResponse", fields={"event_id": serializers.CharField(), "status": serializers.CharField()}),\n    tags=["Webhooks"],\n    summary="Trigger webhook event manually",\n)\ndef trigger_event(request):'
        )
    write(wh, c)

# =====================================================================
# Fix accounts/views.py - UserViewSet queryset guard
# =====================================================================
av = "abia/accounts/views.py"
if os.path.exists(av):
    c = read(av)
    if "class UserViewSet" in c and "swagger_fake_view" not in c:
        if "def get_queryset(self):" in c:
            c = re.sub(
                r'(    def get_queryset\(self\):)',
                r"\1\n        if getattr(self, 'swagger_fake_view', False):\n            return self.queryset.none() if self.queryset else User.objects.none()",
                c
            )
        else:
            c = re.sub(
                r'(class UserViewSet\([^)]+\):)',
                r"\1\n    queryset = User.objects.none()\n\n    def get_queryset(self):\n        if getattr(self, 'swagger_fake_view', False):\n            return User.objects.none()\n        return User.objects.all()",
                c
            )
        write(av, c)

# =====================================================================
# Fix workflows/views.py - WorkflowInstanceViewSet queryset guard
# =====================================================================
wv = "abia/workflows/views.py"
if os.path.exists(wv):
    c = read(wv)
    if "class WorkflowInstanceViewSet" in c and "swagger_fake_view" not in c:
        if "def get_queryset(self):" in c:
            c = re.sub(
                r'(    def get_queryset\(self\):)',
                r"\1\n        if getattr(self, 'swagger_fake_view', False):\n            return WorkflowInstance.objects.none()",
                c
            )
        else:
            c = re.sub(
                r'(class WorkflowInstanceViewSet\([^)]+\):)',
                r"\1\n    queryset = WorkflowInstance.objects.none()\n\n    def get_queryset(self):\n        if getattr(self, 'swagger_fake_view', False):\n            return WorkflowInstance.objects.none()\n        return WorkflowInstance.objects.all()",
                c
            )
        write(wv, c)

# =====================================================================
# Fix ENUM_NAME_OVERRIDES in settings
# =====================================================================
sp = "abia/settings.py"
if os.path.exists(sp):
    c = read(sp)
    if "ENUM_NAME_OVERRIDES" not in c:
        c = c.replace(
            "'COMPONENT_SPLIT_REQUEST': True,",
            "'COMPONENT_SPLIT_REQUEST': True,\n    'ENUM_NAME_OVERRIDES': {\n        'StatusEnum': 'abia.cases.models.CaseStatus',\n        'MigrantStatusEnum': 'abia.migrants.models.MigrantStatus',\n        'UserRoleEnum': 'abia.accounts.models.UserRole',\n    },"
        )
        write(sp, c)

print("\nDone. Run: python3 manage.py spectacular --file /tmp/schema.yml --validate")#!/usr/bin/env python3
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
