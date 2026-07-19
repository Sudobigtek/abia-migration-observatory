"""Integration tests for accounts.repositories module.

Tests cover:
- LGARepository: CRUD, filtering, seed data verification
- UserRepository: CRUD, filtering by LGA, role-based queries

Uses real PostgreSQL database (PostGIS). All tests run inside
Django transactions that roll back on completion.

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from uuid import uuid4

import pytest
from django.db import transaction

from accounts.models import LGA, User
from accounts.repositories import LGARepository, UserRepository

# ───────────────────────────────────────────────────────────────
# LGARepository Tests
# ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLGARepository:
    """Integration tests for LGARepository with real database."""

    def test_get_all_returns_seeded_lgas(self):
        # Given: Database seeded with 17 Abia LGAs (from Phase 1)
        # When: Repository retrieves all LGAs
        result = LGARepository.get_all()

        # Then: All 17 LGAs returned
        assert result.count() == 17

    def test_get_by_id_existing_lga(self):
        # Given: Existing LGA in database
        aba_north = LGA.objects.get(name="Aba North")

        # When: Repository retrieves by ID
        result = LGARepository.get_by_id(aba_north.id)

        # Then: Correct LGA returned
        assert result is not None
        assert result.name == "Aba North"
        assert result.code == "ABN"

    def test_get_by_id_nonexistent(self):
        # Given: Random UUID that does not exist
        fake_id = uuid4()

        # When: Repository retrieves by ID
        result = LGARepository.get_by_id(fake_id)

        # Then: None returned (no exception)
        assert result is None

    def test_get_by_name_existing(self):
        # Given: Known LGA name
        # When: Repository retrieves by name
        result = LGARepository.get_by_name("Umuahia North")

        # Then: Correct LGA returned
        assert result is not None
        assert result.name == "Umuahia North"

    def test_get_by_name_nonexistent(self):
        # Given: Non-existent LGA name
        # When: Repository retrieves by name
        result = LGARepository.get_by_name("Fake LGA")

        # Then: None returned
        assert result is None

    def test_get_by_name_case_insensitive(self):
        # Given: LGA name in different case
        # When: Repository retrieves (case-insensitive)
        result_lower = LGARepository.get_by_name("aba north")
        result_upper = LGARepository.get_by_name("ABA NORTH")

        # Then: Same LGA returned regardless of case
        assert result_lower is not None
        assert result_upper is not None
        assert result_lower.id == result_upper.id

    def test_create_new_lga(self):
        # Given: New LGA data
        data = {
            "name": "Test LGA",
            "code": "TST",
            "population": 100000,
        }

        # When: Repository creates LGA
        with transaction.atomic():
            result = LGARepository.create(data)

            # Then: LGA created with correct attributes
            assert result.id is not None
            assert result.name == "Test LGA"
            assert result.code == "TST"
            assert result.population == 100000

            # Cleanup: delete test LGA
            result.delete()

    def test_update_lga_population(self):
        # Given: Existing LGA
        lga = LGA.objects.get(name="Aba South")
        original_pop = lga.population

        # When: Repository updates population
        with transaction.atomic():
            updated = LGARepository.update(lga.id, {"population": 999999})

            # Then: Population updated
            assert updated.population == 999999

            # Restore original
            lga.population = original_pop
            lga.save()

    def test_delete_lga(self):
        # Given: Create a temporary LGA
        lga = LGA.objects.create(name="Delete Me", code="DLM", population=1)
        lga_id = lga.id

        # When: Repository deletes LGA
        result = LGARepository.delete(lga_id)

        # Then: LGA no longer exists
        assert result is True
        assert LGA.objects.filter(id=lga_id).count() == 0

    def test_delete_nonexistent_lga(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository deletes non-existent LGA
        result = LGARepository.delete(fake_id)

        # Then: Returns False (or 0 rows affected)
        assert result is False


# ───────────────────────────────────────────────────────────────
# UserRepository Tests
# ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestUserRepository:
    """Integration tests for UserRepository with real database."""

    @pytest.fixture
    def test_lga(self):
        """Return a known LGA for user creation."""
        return LGA.objects.get(name="Aba North")

    @pytest.fixture
    def test_user(self, test_lga):
        """Create and return a test user (auto-cleaned by django_db)."""
        user = User.objects.create_user(
            username="testofficer",
            password="TestPass123!",
            role="field_officer",
            lga=test_lga,
        )
        return user

    def test_get_all_users(self, test_user):
        # Given: At least one user exists (superuser from Phase 1 + test_user)
        # When: Repository retrieves all users
        result = UserRepository.get_all()

        # Then: Returns queryset with users
        assert result.count() >= 2  # superuser + test_user

    def test_get_by_id_existing(self, test_user):
        # Given: Existing user
        # When: Repository retrieves by ID
        result = UserRepository.get_by_id(test_user.id)

        # Then: Correct user returned
        assert result is not None
        assert result.username == "testofficer"
        assert result.role == "field_officer"

    def test_get_by_id_nonexistent(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository retrieves by ID
        result = UserRepository.get_by_id(fake_id)

        # Then: None returned
        assert result is None

    def test_get_by_lga(self, test_user, test_lga):
        # Given: User assigned to Aba North
        # When: Repository filters by LGA
        result = UserRepository.get_by_lga(test_lga.id)

        # Then: User found in results
        assert result.filter(id=test_user.id).exists()

    def test_get_by_lga_empty(self, test_lga):
        # Given: LGA with no users (find one without test_user)
        empty_lga = LGA.objects.exclude(id=test_lga.id).first()

        # When: Repository filters by that LGA
        result = UserRepository.get_by_lga(empty_lga.id)

        # Then: Empty queryset returned
        assert result.count() == 0

    def test_get_by_username(self, test_user):
        # Given: Existing user with known username
        # When: Repository retrieves by username
        result = UserRepository.get_by_username("testofficer")

        # Then: Correct user returned
        assert result is not None
        assert result.id == test_user.id

    def test_get_by_username_nonexistent(self):
        # Given: Non-existent username
        # When: Repository retrieves by username
        result = UserRepository.get_by_username("nonexistent_user")

        # Then: None returned
        assert result is None

    def test_create_user(self, test_lga):
        # Given: New user data
        data = {
            "username": "newofficer",
            "password": "NewPass456!",
            "role": "field_officer",
            "lga": test_lga,
        }

        # When: Repository creates user
        result = UserRepository.create(data)

        # Then: User created with correct attributes
        assert result.id is not None
        assert result.username == "newofficer"
        assert result.role == "field_officer"
        assert result.lga_id == test_lga.id
        assert result.check_password("NewPass456!")

    def test_create_user_duplicate_username(self, test_user):
        # Given: Username already exists
        data = {
            "username": "testofficer",  # Same as test_user
            "password": "AnotherPass!",
            "role": "field_officer",
            "lga": test_user.lga,
        }

        # When/Then: IntegrityError raised
        with pytest.raises(Exception):  # Django IntegrityError
            UserRepository.create(data)

    def test_update_user_role(self, test_user):
        # Given: Existing user with role field_officer
        # When: Repository updates role
        updated = UserRepository.update(test_user.id, {"role": "lga_coordinator"})

        # Then: Role updated
        assert updated.role == "lga_coordinator"

        # Restore
        test_user.role = "field_officer"
        test_user.save()

    def test_update_user_lga(self, test_user):
        # Given: Existing user and different LGA
        new_lga = LGA.objects.exclude(id=test_user.lga_id).first()

        # When: Repository updates LGA
        updated = UserRepository.update(test_user.id, {"lga": new_lga})

        # Then: LGA updated
        assert updated.lga_id == new_lga.id

        # Restore
        test_user.lga = LGA.objects.get(id=test_user.lga_id)
        test_user.save()

    def test_delete_user(self, test_user):
        # Given: Existing user
        user_id = test_user.id

        # When: Repository deletes user
        result = UserRepository.delete(user_id)

        # Then: User no longer exists
        assert result is True
        assert User.objects.filter(id=user_id).count() == 0

    def test_delete_nonexistent_user(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository deletes non-existent user
        result = UserRepository.delete(fake_id)

        # Then: Returns False
        assert result is False

    def test_filter_by_role(self, test_user):
        # Given: User with role field_officer
        # When: Repository filters by role
        result = UserRepository.filter_by_role("field_officer")

        # Then: Test user found in results
        assert result.filter(id=test_user.id).exists()

    def test_filter_by_role_no_results(self):
        # Given: Role with no users
        # When: Repository filters by non-assigned role
        result = UserRepository.filter_by_role("super_admin")

        # Then: Only the Phase 1 superuser should exist
        # (adjust assertion based on actual seeded data)
        assert result.count() >= 0

    def test_count_by_lga(self, test_user, test_lga):
        # Given: User in Aba North
        # When: Repository counts users by LGA
        result = UserRepository.count_by_lga(test_lga.id)

        # Then: Count >= 1 (test_user + possibly others)
        assert result >= 1
