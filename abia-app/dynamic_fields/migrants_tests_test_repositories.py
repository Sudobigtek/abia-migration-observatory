"""Integration tests for migrants.repositories module.

Tests cover:
- MigrantRepository: CRUD, search, filtering, duplicate detection
- Real database operations with PostgreSQL + PostGIS

Per Architecture Contract §8.1: Integration tests = 15% of pyramid.
"""

from datetime import date
from uuid import uuid4

import pytest

from accounts.models import LGA
from migrants.models import Migrant
from migrants.repositories import MigrantRepository


@pytest.fixture
def test_lga():
    """Return a known LGA for migrant creation."""
    return LGA.objects.get(name="Aba North")


@pytest.fixture
def test_lga_2():
    """Return a second LGA for cross-LGA tests."""
    return LGA.objects.get(name="Aba South")


@pytest.fixture
def test_migrant(test_lga):
    """Create and return a test migrant."""
    migrant = Migrant.objects.create(
        full_name="John Doe",
        phone="+2348012345678",
        date_of_birth=date(1990, 5, 15),
        current_lga=test_lga,
        lga_of_origin=test_lga,
        status="active",
    )
    return migrant


@pytest.mark.django_db
class TestMigrantRepository:
    """Integration tests for MigrantRepository with real database."""

    def test_get_all_migrants(self, test_migrant):
        # Given: At least one migrant exists
        # When: Repository retrieves all
        result = MigrantRepository.get_all()

        # Then: Returns queryset with migrants
        assert result.count() >= 1
        assert result.filter(id=test_migrant.id).exists()

    def test_get_by_id_existing(self, test_migrant):
        # Given: Existing migrant
        # When: Repository retrieves by ID
        result = MigrantRepository.get_by_id(test_migrant.id)

        # Then: Correct migrant returned
        assert result is not None
        assert result.full_name == "John Doe"
        assert result.phone == "+2348012345678"

    def test_get_by_id_nonexistent(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository retrieves by ID
        result = MigrantRepository.get_by_id(fake_id)

        # Then: None returned
        assert result is None

    def test_get_by_lga(self, test_migrant, test_lga):
        # Given: Migrant in Aba North
        # When: Repository filters by LGA
        result = MigrantRepository.get_by_lga(test_lga.id)

        # Then: Migrant found in results
        assert result.filter(id=test_migrant.id).exists()

    def test_get_by_lga_empty(self, test_lga_2):
        # Given: LGA with no migrants (Aba South, assuming clean state)
        # When: Repository filters by that LGA
        result = MigrantRepository.get_by_lga(test_lga_2.id)

        # Then: Empty queryset returned
        assert result.count() == 0

    def test_get_by_phone_existing(self, test_migrant):
        # Given: Existing phone number
        # When: Repository retrieves by phone
        result = MigrantRepository.get_by_phone("+2348012345678")

        # Then: Correct migrant returned
        assert result is not None
        assert result.id == test_migrant.id

    def test_get_by_phone_nonexistent(self):
        # Given: Non-existent phone number
        # When: Repository retrieves by phone
        result = MigrantRepository.get_by_phone("+2348000000000")

        # Then: None returned
        assert result is None

    def test_create_migrant(self, test_lga):
        # Given: New migrant data
        data = {
            "full_name": "Jane Smith",
            "phone": "+2348098765432",
            "date_of_birth": date(1985, 3, 20),
            "current_lga": test_lga,
            "lga_of_origin": test_lga,
            "status": "active",
        }

        # When: Repository creates migrant
        result = MigrantRepository.create(data)

        # Then: Migrant created with correct attributes
        assert result.id is not None
        assert result.full_name == "Jane Smith"
        assert result.phone == "+2348098765432"
        assert result.current_lga_id == test_lga.id

    def test_create_migrant_duplicate_phone(self, test_migrant, test_lga):
        # Given: Phone number already exists
        data = {
            "full_name": "Duplicate Phone",
            "phone": "+2348012345678",  # Same as test_migrant
            "date_of_birth": date(2000, 1, 1),
            "current_lga": test_lga,
            "lga_of_origin": test_lga,
            "status": "active",
        }

        # When/Then: IntegrityError raised (if phone is unique)
        with pytest.raises(Exception):
            MigrantRepository.create(data)

    def test_update_migrant_full_name(self, test_migrant):
        # Given: Existing migrant
        # When: Repository updates full_name
        updated = MigrantRepository.update(
            test_migrant.id, {"full_name": "Updated Name"}
        )

        # Then: Name updated
        assert updated.full_name == "Updated Name"

    def test_update_migrant_status(self, test_migrant):
        # Given: Existing migrant with status active
        # When: Repository updates status
        updated = MigrantRepository.update(test_migrant.id, {"status": "inactive"})

        # Then: Status updated
        assert updated.status == "inactive"

        # Restore
        test_migrant.status = "active"
        test_migrant.save()

    def test_update_migrant_lga(self, test_migrant, test_lga_2):
        # Given: Existing migrant and different LGA
        # When: Repository updates current_lga
        updated = MigrantRepository.update(test_migrant.id, {"current_lga": test_lga_2})

        # Then: LGA updated
        assert updated.current_lga_id == test_lga_2.id

        # Restore
        test_migrant.current_lga = test_lga
        test_migrant.save()

    def test_update_nonexistent_migrant(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository updates non-existent migrant
        result = MigrantRepository.update(fake_id, {"full_name": "Ghost"})

        # Then: Returns None (or raises not found)
        assert result is None

    def test_delete_migrant(self, test_migrant):
        # Given: Existing migrant
        migrant_id = test_migrant.id

        # When: Repository deletes migrant
        result = MigrantRepository.delete(migrant_id)

        # Then: Migrant no longer exists
        assert result is True
        assert Migrant.objects.filter(id=migrant_id).count() == 0

    def test_delete_nonexistent_migrant(self):
        # Given: Random UUID
        fake_id = uuid4()

        # When: Repository deletes non-existent migrant
        result = MigrantRepository.delete(fake_id)

        # Then: Returns False
        assert result is False

    def test_search_by_name(self, test_migrant):
        # Given: Migrant named "John Doe"
        # When: Repository searches by name
        result = MigrantRepository.search_by_name("John")

        # Then: Migrant found
        assert result.filter(id=test_migrant.id).exists()

    def test_search_by_name_no_results(self):
        # Given: Search term that matches nothing
        # When: Repository searches
        result = MigrantRepository.search_by_name("XYZNONEXISTENT")

        # Then: Empty queryset
        assert result.count() == 0

    def test_search_by_name_in_lga(self, test_migrant, test_lga):
        # Given: Migrant in Aba North named "John Doe"
        # When: Repository searches by name in specific LGA
        result = MigrantRepository.search_by_name_in_lga("John", test_lga.id)

        # Then: Migrant found
        assert result.filter(id=test_migrant.id).exists()

    def test_filter_by_status(self, test_migrant):
        # Given: Migrant with status "active"
        # When: Repository filters by status
        result = MigrantRepository.filter_by_status("active")

        # Then: Migrant found
        assert result.filter(id=test_migrant.id).exists()

    def test_filter_by_status_no_results(self, test_migrant):
        # Given: Migrant with status "active"
        # When: Repository filters by different status
        result = MigrantRepository.filter_by_status("inactive")

        # Then: Empty queryset (assuming no inactive migrants)
        assert result.count() == 0

    def test_filter_by_status_in_lga(self, test_migrant, test_lga):
        # Given: Active migrant in Aba North
        # When: Repository filters by status in LGA
        result = MigrantRepository.filter_by_status_in_lga("active", test_lga.id)

        # Then: Migrant found
        assert result.filter(id=test_migrant.id).exists()

    def test_count_by_lga(self, test_migrant, test_lga):
        # Given: Migrant in Aba North
        # When: Repository counts by LGA
        result = MigrantRepository.count_by_lga(test_lga.id)

        # Then: Count >= 1
        assert result >= 1

    def test_count_by_lga_empty(self, test_lga_2):
        # Given: LGA with no migrants
        # When: Repository counts by LGA
        result = MigrantRepository.count_by_lga(test_lga_2.id)

        # Then: Count == 0
        assert result == 0

    def test_count_all(self, test_migrant):
        # Given: At least one migrant
        # When: Repository counts all
        result = MigrantRepository.count_all()

        # Then: Count >= 1
        assert result >= 1
