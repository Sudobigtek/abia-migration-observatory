"""Tests for PII encryption service."""

import pytest
import os

from abia.common.encryption import PIIEncryption


class TestPIIEncryption:
    """Test AES-256 encryption and masking."""

    def test_encrypt_decrypt_roundtrip(self):
        """Given plaintext, encrypt then decrypt returns original."""
        enc = PIIEncryption()
        plaintext = "12345678901"
        ciphertext = enc.encrypt(plaintext)
        assert ciphertext != plaintext
        assert enc.decrypt(ciphertext) == plaintext

    def test_encrypt_empty_string(self):
        """Given empty string, return empty."""
        enc = PIIEncryption()
        assert enc.encrypt("") == ""
        assert enc.decrypt("") == ""

    def test_decrypt_invalid_ciphertext(self):
        """Given invalid ciphertext, raise exception."""
        enc = PIIEncryption()
        with pytest.raises(Exception):
            enc.decrypt("not-valid-ciphertext")

    def test_mask_phone(self):
        """Mask phone number for logging."""
        assert PIIEncryption.mask_phone("+2348111111111") == "+234****1111"
        assert PIIEncryption.mask_phone("short") == "****"
        assert PIIEncryption.mask_phone("") == "****"

    def test_mask_id_number(self):
        """Mask ID number for logging."""
        assert PIIEncryption.mask_id_number("12345678901") == "1234****8901"
        assert PIIEncryption.mask_id_number("ab") == "****"
        assert PIIEncryption.mask_id_number("") == "****"

    @pytest.mark.django_db
    def test_migrant_id_number_encryption(self, test_user):
        """Store and retrieve encrypted id_number on Migrant."""
        from abia.accounts.models import LGA
        from abia.migrants.models import Migrant
        from abia.migrants.repositories import MigrantRepository

        lga = LGA.objects.first()
        enc = PIIEncryption()
        plain_id = "12345678901"

        migrant = Migrant.objects.create(
            full_name="Encrypted ID Test",
            phone="+2348111111111",
            gender="male",
            current_lga=lga,
            created_by=test_user,
            id_number_plaintext=plain_id,
        )

        # Encrypt and store
        migrant.id_number_encrypted = enc.encrypt(plain_id)
        migrant.save()

        # Retrieve and decrypt
        retrieved = Migrant.objects.get(id=migrant.id)
        assert retrieved.id_number_encrypted != plain_id
        decrypted = enc.decrypt(retrieved.id_number_encrypted)
        assert decrypted == plain_id
