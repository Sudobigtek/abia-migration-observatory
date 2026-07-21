import os
import pytest

def pytest_collection_modifyitems(config, items):
    skip_paths = [
        os.path.join(os.path.dirname(__file__), "dynamic_fields"),
        os.path.join(os.path.dirname(__file__), "dynamic_fields_backup_47470"),
    ]
    for item in list(items):
        for skip in skip_paths:
            if str(item.fspath).startswith(skip):
                items.remove(item)
                break

import pytest
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, date

User = get_user_model()

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="testadmin", password="testpass", email="admin@test.gov.ng"
    )

@pytest.fixture
def field_officer(db):
    return User.objects.create_user(
        username="fieldofficer", password="testpass", role="field_officer"
    )
