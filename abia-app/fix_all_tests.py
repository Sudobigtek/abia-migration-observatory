#!/usr/bin/env python3
"""
Abia Migration Observatory - Complete Test File Generator
Run on WSL host: python3 fix_all_tests.py
Creates all test files, __init__.py files, pytest.ini, and common/exceptions.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def write_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    print("  [OK] " + path)


print("=" * 60)
print("ABIA MIGRATION OBSERVATORY - TEST FILE GENERATOR")
print("=" * 60)
print("Target directory: " + BASE_DIR)
print()

# =============================================================================
# FILE 1: common/exceptions.py
# =============================================================================
write_file(
    "common/exceptions.py",
    """
class AbiaBaseException(Exception):
    def __init__(self, message, code="abia_error", status_code=500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class LGANotFoundError(AbiaBaseException):
    def __init__(self, identifier):
        super().__init__(f"LGA not found: {identifier}", "lga_not_found", 404)


class LGAAccessDenied(AbiaBaseException):
    def __init__(self, message="Access denied"):
        super().__init__(message, "lga_access_denied", 403)


class UserNotFoundError(AbiaBaseException):
    def __init__(self, uid):
        super().__init__(f"User not found: {uid}", "user_not_found", 404)


class InvalidRoleError(AbiaBaseException):
    def __init__(self, role):
        super().__init__(f"Invalid role: {role}", "invalid_role", 422)


class MigrantNotFoundError(AbiaBaseException):
    def __init__(self, mid):
        super().__init__(f"Migrant not found: {mid}", "migrant_not_found", 404)


class DuplicateMigrantError(AbiaBaseException):
    def __init__(self, phone):
        super().__init__(f"Migrant with phone {phone} already exists", "duplicate_migrant", 409)


class InvalidPhoneError(AbiaBaseException):
    def __init__(self, phone):
        super().__init__(f"Invalid phone number: {phone}", "invalid_phone", 422)


class CaseNotFoundError(AbiaBaseException):
    def __init__(self, cid):
        super().__init__(f"Case not found: {cid}", "case_not_found", 404)


class InvalidStatusTransitionError(AbiaBaseException):
    def __init__(self, fr, to):
        super().__init__(f"Invalid transition: {fr} -> {to}", "invalid_status_transition", 422)


class InvalidPriorityError(AbiaBaseException):
    def __init__(self, p):
        super().__init__(f"Invalid priority: {p}", "invalid_priority", 422)


class ReferralNotFoundError(AbiaBaseException):
    def __init__(self, rid):
        super().__init__(f"Referral not found: {rid}", "referral_not_found", 404)


class InvalidReferralStatusError(AbiaBaseException):
    def __init__(self, fr, to):
        super().__init__(f"Invalid referral transition: {fr} -> {to}", "invalid_referral_status", 422)


class SelfReferralError(AbiaBaseException):
    def __init__(self, lga_id):
        super().__init__(f"Cannot create referral within same LGA: {lga_id}", "self_referral", 422)


class ValidationError(AbiaBaseException):
    def __init__(self, message, field=None):
        super().__init__(f"Validation error: {message}", "validation_error", 400)
""",
)

# =============================================================================
# FILE 2-5: __init__.py files
# =============================================================================
for app in ["accounts", "migrants", "cases", "referrals"]:
    write_file(app + "/tests/__init__.py", "")

# =============================================================================
# FILE 6: pytest.ini
# =============================================================================
write_file(
    "pytest.ini",
    """[pytest]
DJANGO_SETTINGS_MODULE = abia.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""",
)

# =============================================================================
# FILE 7: accounts/tests/test_repositories.py
# =============================================================================
write_file(
    "accounts/tests/test_repositories.py",
    """
import pytest
from uuid import uuid4
from abia.accounts.models import LGA, User
from abia.accounts.repositories import LGARepository, UserRepository


@pytest.mark.django_db
class TestLGARepository:
    def test_get_all_returns_seeded_lgas(self):
        result = LGARepository.get_all()
        assert result.count() == 17

    def test_get_by_id_existing_lga(self):
        aba_north = LGA.objects.get(name="Aba North")
        result = LGARepository.get_by_id(aba_north.id)
        assert result is not None
        assert result.name == "Aba North"
        assert result.code == "ABN"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = LGARepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_code_existing(self):
        result = LGARepository.get_by_code("ABN")
        assert result is not None
        assert result.name == "Aba North"

    def test_get_by_code_nonexistent(self):
        result = LGARepository.get_by_code("XXX")
        assert result is None


@pytest.mark.django_db
class TestUserRepository:
    def test_get_all_users(self):
        result = UserRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self):
        user = User.objects.first()
        result = UserRepository.get_by_id(user.id)
        assert result is not None

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = UserRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self):
        lga = LGA.objects.first()
        result = UserRepository.get_by_lga(lga.id)
        assert result.count() >= 0

    def test_get_by_username_existing(self):
        user = User.objects.first()
        result = UserRepository.get_by_username(user.username)
        assert result is not None

    def test_get_by_username_nonexistent(self):
        result = UserRepository.get_by_username("nonexistent_xyz")
        assert result is None

    def test_create_user(self):
        lga = LGA.objects.first()
        data = {
            "username": "testuser_repo",
            "password": "TestPass123!",
            "role": "field_officer",
            "lga": lga,
        }
        result = UserRepository.create(data)
        assert result.id is not None
        assert result.username == "testuser_repo"

    def test_create_superuser(self):
        lga = LGA.objects.first()
        data = {
            "username": "superuser_repo",
            "password": "SuperPass123!",
            "role": "super_admin",
            "lga": lga,
        }
        result = UserRepository.create_superuser(data)
        assert result.id is not None
        assert result.is_superuser is True
""",
)

# =============================================================================
# FILE 8: migrants/tests/test_repositories.py
# =============================================================================
write_file(
    "migrants/tests/test_repositories.py",
    """
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.migrants.repositories import MigrantRepository


@pytest.fixture
def test_lga():
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_migrant(test_lga):
    return Migrant.objects.create(
        full_name="Test Migrant",
        phone="+2348011111111",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )


@pytest.mark.django_db
class TestMigrantRepository:
    def test_get_all_migrants(self, test_migrant):
        result = MigrantRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_migrant):
        result = MigrantRepository.get_by_id(test_migrant.id)
        assert result is not None
        assert result.full_name == "Test Migrant"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = MigrantRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_migrant, test_lga):
        result = MigrantRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_migrant.id).exists()

    def test_create_migrant(self, test_lga):
        data = {
            "full_name": "New Migrant",
            "phone": "+2348022222222",
            "date_of_birth": date(1985, 5, 15),
            "gender": "female",
            "current_lga": test_lga,
            "lga_of_origin": test_lga,
            "status": "active",
        }
        result = MigrantRepository.create(data)
        assert result.id is not None
        assert result.full_name == "New Migrant"

    def test_update_migrant(self, test_migrant):
        updated = MigrantRepository.update(test_migrant.id, {"full_name": "Updated Name"})
        assert updated.full_name == "Updated Name"
""",
)

# =============================================================================
# FILE 9: cases/tests/test_repositories.py
# =============================================================================
write_file(
    "cases/tests/test_repositories.py",
    """
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.cases.repositories import CaseRepository


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


@pytest.fixture
def test_case(test_user, test_migrant, test_lga):
    return Case.objects.create(
        migrant=test_migrant,
        lga=test_lga,
        assigned_to=test_user,
        created_by=test_user,
        status="open",
        priority="medium",
        case_type="protection",
        description="Test case",
    )


@pytest.mark.django_db
class TestCaseRepository:
    def test_get_all_cases(self, test_case):
        result = CaseRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_case):
        result = CaseRepository.get_by_id(test_case.id)
        assert result is not None
        assert result.description == "Test case"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = CaseRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_case, test_lga):
        result = CaseRepository.get_by_lga(test_lga.id)
        assert result.filter(id=test_case.id).exists()

    def test_get_by_migrant(self, test_case, test_migrant):
        result = CaseRepository.get_by_migrant(test_migrant.id)
        assert result.filter(id=test_case.id).exists()

    def test_create_case(self, test_user, test_migrant, test_lga):
        data = {
            "migrant": test_migrant,
            "lga": test_lga,
            "assigned_to": test_user,
            "created_by": test_user,
            "status": "open",
            "priority": "high",
            "case_type": "medical",
            "description": "New case",
        }
        result = CaseRepository.create(data)
        assert result.id is not None
        assert result.priority == "high"

    def test_update_case(self, test_case):
        updated = CaseRepository.update(test_case.id, {"status": "in_progress"})
        assert updated.status == "in_progress"
""",
)

# =============================================================================
# FILE 10: referrals/tests/test_repositories.py
# =============================================================================
write_file(
    "referrals/tests/test_repositories.py",
    """
import pytest
from uuid import uuid4
from datetime import date
from abia.accounts.models import LGA, User
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.referrals.repositories import ReferralRepository


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


@pytest.fixture
def test_referral(test_case, from_lga, to_lga, test_user):
    return Referral.objects.create(
        case=test_case,
        from_lga=from_lga,
        to_lga=to_lga,
        to_organization="Hospital",
        to_contact_name="Dr. Smith",
        to_contact_phone="+2348055555555",
        reason="Medical referral",
        status="pending",
        created_by=test_user,
    )


@pytest.mark.django_db
class TestReferralRepository:
    def test_get_all_referrals(self, test_referral):
        result = ReferralRepository.get_all()
        assert result.count() >= 1

    def test_get_by_id_existing(self, test_referral):
        result = ReferralRepository.get_by_id(test_referral.id)
        assert result is not None
        assert result.reason == "Medical referral"

    def test_get_by_id_nonexistent(self):
        fake_id = uuid4()
        result = ReferralRepository.get_by_id(fake_id)
        assert result is None

    def test_get_by_lga(self, test_referral, from_lga):
        result = ReferralRepository.get_by_lga(from_lga.id)
        assert result.filter(id=test_referral.id).exists()

    def test_get_by_case(self, test_referral, test_case):
        result = ReferralRepository.get_by_case(test_case.id)
        assert result.filter(id=test_referral.id).exists()

    def test_create_referral(self, test_case, from_lga, to_lga, test_user):
        data = {
            "case": test_case,
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Clinic",
            "to_contact_name": "Dr. Jones",
            "to_contact_phone": "+2348066666666",
            "reason": "Follow-up",
            "status": "pending",
            "created_by": test_user,
        }
        result = ReferralRepository.create(data)
        assert result.id is not None
        assert result.to_organization == "Clinic"

    def test_update_referral(self, test_referral):
        updated = ReferralRepository.update(test_referral.id, {"status": "in_progress"})
        assert updated.status == "in_progress"
""",
)

# =============================================================================
# FILE 11: accounts/tests/test_services.py
# =============================================================================
write_file(
    "accounts/tests/test_services.py",
    """
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.accounts.services import LGAService, UserService
from common.exceptions import LGANotFoundError, LGAAccessDenied, UserNotFoundError, InvalidRoleError


class TestLGAService:
    @patch("abia.accounts.services.LGARepository")
    def test_get_all_lgas(self, mock_repo):
        mock_repo.get_all.return_value = [MagicMock(name="Aba North")]
        result = LGAService.get_all()
        assert len(result) == 1

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(name="Aba North")
        result = LGAService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_id(uuid4())

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_code_found(self, mock_repo):
        mock_repo.get_by_code.return_value = MagicMock(name="Aba North")
        result = LGAService.get_by_code("ABN")
        assert result is not None

    @patch("abia.accounts.services.LGARepository")
    def test_get_lga_by_code_not_found(self, mock_repo):
        mock_repo.get_by_code.return_value = None
        with pytest.raises(LGANotFoundError):
            LGAService.get_by_code("XXX")


class TestUserService:
    @patch("abia.accounts.services.UserRepository")
    def test_get_user_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(username="test")
        result = UserService.get_by_id(uuid4())
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_get_user_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            UserService.get_by_id(uuid4())

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_valid_role(self, mock_repo):
        mock_user = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.create.return_value = mock_user
        result = UserService.create({"role": "field_officer", "lga": mock_user.lga}, mock_user)
        assert result.role == "field_officer"

    @patch("abia.accounts.services.UserRepository")
    def test_create_user_invalid_role(self, mock_repo):
        mock_user = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidRoleError):
            UserService.create({"role": "invalid_role", "lga": mock_user.lga}, mock_user)

    @patch("abia.accounts.services.UserRepository")
    def test_field_officer_cannot_create_outside_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        with pytest.raises(LGAAccessDenied):
            UserService.create({"role": "field_officer", "lga": other_lga}, officer)

    @patch("abia.accounts.services.UserRepository")
    def test_state_admin_can_create_any_lga(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        mock_repo.create.return_value = MagicMock(role="field_officer")
        result = UserService.create({"role": "field_officer", "lga": other_lga}, admin)
        assert result is not None

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = UserService.get_users_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.accounts.services.UserRepository")
    def test_get_users_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = UserService.get_users_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()
""",
)

# =============================================================================
# FILE 12: migrants/tests/test_services.py
# =============================================================================
write_file(
    "migrants/tests/test_services.py",
    """
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import date
from abia.migrants.services import MigrantService
from common.exceptions import MigrantNotFoundError, DuplicateMigrantError, InvalidPhoneError, LGAAccessDenied


class TestMigrantServiceGet:
    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrant_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(full_name="John")
        result = MigrantService.get_by_id(uuid4())
        assert result.full_name == "John"

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrant_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(MigrantNotFoundError):
            MigrantService.get_by_id(uuid4())

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = MigrantService.get_migrants_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.migrants.services.MigrantRepository")
    def test_get_migrants_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = MigrantService.get_migrants_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestMigrantServiceCreate:
    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_field_officer_same_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = []
        mock_repo.create.return_value = MagicMock(full_name="Jane")
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        result = MigrantService.create_migrant(data, officer)
        assert result.full_name == "Jane"

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_field_officer_other_lga_denied(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": other_lga,
        }
        with pytest.raises(LGAAccessDenied):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_duplicate_phone(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock(phone="+2348012345678")]
        data = {
            "full_name": "Jane",
            "phone": "+2348012345678",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        with pytest.raises(DuplicateMigrantError):
            MigrantService.create_migrant(data, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_create_migrant_invalid_phone(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = []
        data = {
            "full_name": "Jane",
            "phone": "invalid",
            "date_of_birth": date(1990, 1, 1),
            "gender": "female",
            "current_lga": officer.lga,
        }
        with pytest.raises(InvalidPhoneError):
            MigrantService.create_migrant(data, officer)


class TestMigrantServiceUpdate:
    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(full_name="New")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)
        assert result.full_name == "New"

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(MigrantNotFoundError):
            MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)

    @patch("abia.migrants.services.MigrantRepository")
    def test_update_migrant_field_officer_other_lga_denied(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(full_name="Old", current_lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            MigrantService.update_migrant(uuid4(), {"full_name": "New"}, officer)
""",
)

# =============================================================================
# FILE 13: cases/tests/test_services.py
# =============================================================================
write_file(
    "cases/tests/test_services.py",
    """
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.cases.services import CaseService
from common.exceptions import CaseNotFoundError, InvalidStatusTransitionError, InvalidPriorityError, LGAAccessDenied


class TestCaseServiceGet:
    @patch("abia.cases.services.CaseRepository")
    def test_get_case_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(description="Test")
        result = CaseService.get_by_id(uuid4())
        assert result.description == "Test"

    @patch("abia.cases.services.CaseRepository")
    def test_get_case_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CaseNotFoundError):
            CaseService.get_by_id(uuid4())

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = CaseService.get_cases_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.cases.services.CaseRepository")
    def test_get_cases_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = CaseService.get_cases_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestCaseServiceCreate:
    @patch("abia.cases.services.CaseRepository")
    def test_create_case_field_officer_same_lga(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.create.return_value = MagicMock(priority="high")
        data = {
            "migrant": MagicMock(),
            "lga": officer.lga,
            "priority": "high",
            "case_type": "medical",
            "description": "New case",
        }
        result = CaseService.create_case(data, officer)
        assert result.priority == "high"

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_field_officer_other_lga_denied(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        other_lga = MagicMock(id=uuid4())
        data = {
            "migrant": MagicMock(),
            "lga": other_lga,
            "priority": "high",
            "case_type": "medical",
            "description": "New case",
        }
        with pytest.raises(LGAAccessDenied):
            CaseService.create_case(data, officer)

    @patch("abia.cases.services.CaseRepository")
    def test_create_case_invalid_priority(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        data = {
            "migrant": MagicMock(),
            "lga": officer.lga,
            "priority": "invalid",
            "case_type": "medical",
            "description": "New case",
        }
        with pytest.raises(InvalidPriorityError):
            CaseService.create_case(data, officer)


class TestCaseServiceStatusTransitions:
    @patch("abia.cases.services.CaseRepository")
    def test_valid_transition_open_to_in_progress(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(status="in_progress")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = CaseService.update_status(uuid4(), "in_progress", officer)
        assert result.status == "in_progress"

    @patch("abia.cases.services.CaseRepository")
    def test_invalid_transition_open_to_resolved(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=MagicMock(id=uuid4()))
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidStatusTransitionError):
            CaseService.update_status(uuid4(), "resolved", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_field_officer_cannot_update_other_lga_case(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            CaseService.update_status(uuid4(), "in_progress", officer)

    @patch("abia.cases.services.CaseRepository")
    def test_state_admin_can_update_any_case(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="open", lga=other_lga)
        mock_repo.update.return_value = MagicMock(status="in_progress")
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        result = CaseService.update_status(uuid4(), "in_progress", admin)
        assert result.status == "in_progress"
""",
)

# =============================================================================
# FILE 14: referrals/tests/test_services.py
# =============================================================================
write_file(
    "referrals/tests/test_services.py",
    """
import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from abia.referrals.services import ReferralService
from common.exceptions import ReferralNotFoundError, InvalidReferralStatusError, SelfReferralError, LGAAccessDenied


class TestReferralServiceGet:
    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referral_by_id_found(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(reason="Medical")
        result = ReferralService.get_by_id(uuid4())
        assert result.reason == "Medical"

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referral_by_id_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ReferralNotFoundError):
            ReferralService.get_by_id(uuid4())

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_field_officer(self, mock_repo):
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        mock_repo.get_by_lga.return_value = [MagicMock()]
        result = ReferralService.get_referrals_for_request(MagicMock(user=officer))
        mock_repo.get_by_lga.assert_called_once()

    @patch("abia.referrals.services.ReferralRepository")
    def test_get_referrals_for_request_state_admin(self, mock_repo):
        admin = MagicMock(role="state_admin", lga=MagicMock(id=uuid4()))
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]
        result = ReferralService.get_referrals_for_request(MagicMock(user=admin))
        mock_repo.get_all.assert_called_once()


class TestReferralServiceCreate:
    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_valid(self, mock_repo):
        from_lga = MagicMock(id=uuid4())
        to_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=from_lga)
        mock_repo.create.return_value = MagicMock(status="pending")
        data = {
            "case": MagicMock(),
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        result = ReferralService.create_referral(data, officer)
        assert result.status == "pending"

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_self_referral(self, mock_repo):
        same_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=same_lga)
        data = {
            "case": MagicMock(),
            "from_lga": same_lga,
            "to_lga": same_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        with pytest.raises(SelfReferralError):
            ReferralService.create_referral(data, officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_create_referral_field_officer_from_other_lga_denied(self, mock_repo):
        officer_lga = MagicMock(id=uuid4())
        from_lga = MagicMock(id=uuid4())
        to_lga = MagicMock(id=uuid4())
        officer = MagicMock(role="field_officer", lga=officer_lga)
        data = {
            "case": MagicMock(),
            "from_lga": from_lga,
            "to_lga": to_lga,
            "to_organization": "Hospital",
            "reason": "Medical",
            "status": "pending",
        }
        with pytest.raises(LGAAccessDenied):
            ReferralService.create_referral(data, officer)


class TestReferralServiceStatusTransitions:
    @patch("abia.referrals.services.ReferralRepository")
    def test_accept_pending_referral(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=MagicMock(id=uuid4()))
        mock_repo.update.return_value = MagicMock(status="accepted")
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        result = ReferralService.update_status(uuid4(), "accepted", officer)
        assert result.status == "accepted"

    @patch("abia.referrals.services.ReferralRepository")
    def test_invalid_transition_pending_to_completed(self, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=MagicMock(id=uuid4()))
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(InvalidReferralStatusError):
            ReferralService.update_status(uuid4(), "completed", officer)

    @patch("abia.referrals.services.ReferralRepository")
    def test_field_officer_cannot_update_other_lga_referral(self, mock_repo):
        other_lga = MagicMock(id=uuid4())
        mock_repo.get_by_id.return_value = MagicMock(status="pending", from_lga=other_lga)
        officer = MagicMock(role="field_officer", lga=MagicMock(id=uuid4()))
        with pytest.raises(LGAAccessDenied):
            ReferralService.update_status(uuid4(), "accepted", officer)
""",
)

print()
print("=" * 60)
print("ALL 14 FILES CREATED SUCCESSFULLY")
print("=" * 60)
print()
print("Next steps:")
print("  1. Re-enter container:")
print("     docker run -it --rm \\")
print("       -v $(pwd):/app -w /app \\")
print("       --network abia-migration-observatory_abia-network \\")
print("       -e POSTGRES_PASSWORD=5ZEyItPKrE07Naj3emXOBvkR/xjWNUWisg3svy+d+Ig= \\")
print("       abia-django:latest bash")
print()
print("  2. Inside container, install pytest:")
print("     pip install --default-timeout=300 pytest pytest-django")
print("     export DJANGO_SETTINGS_MODULE=abia.settings")
print()
print("  3. Run tests:")
print("     python3 -m pytest accounts/tests/test_repositories.py -v")
print("     python3 -m pytest -v")
print()
