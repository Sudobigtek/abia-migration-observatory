"""PII encryption and masking for Abia Migration Observatory.

Per Architecture Contract §10.2:
- id_number (NIN, passport) → AES-256 encryption at rest
- phone → masked in logs, encrypted in backups

DEV FALLBACK: Uses hashlib + base64 for deterministic encryption.
PRODUCTION: Must install 'cryptography' and use Fernet or AWS KMS.
"""

import base64
import hashlib
import hmac
import logging
import os
import secrets

logger = logging.getLogger("abia.encryption")

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTOGRAPHY = True
except ImportError:
    _HAS_CRYPTOGRAPHY = False
    logger.warning(
        "cryptography not installed. Using dev fallback encryption. "
        "Install 'cryptography' for production AES-256-GCM."
    )


class PIIEncryption:
    """Encrypt and decrypt PII fields."""

    _instance = None
    _key = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_key()
        return cls._instance

    def _init_key(self):
        """Initialize encryption key from env or Django SECRET_KEY."""
        key = os.environ.get("PII_ENCRYPTION_KEY")
        if not key:
            secret = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
            key = base64.urlsafe_b64encode(
                hashlib.sha256(secret.encode()).digest()
            ).decode()
        self._key = key.encode() if isinstance(key, str) else key

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 32-byte key using PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac("sha256", self._key, salt, 100000, dklen=32)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext. Returns base64(salt + ciphertext + mac)."""
        if not plaintext:
            return ""
        if _HAS_CRYPTOGRAPHY:
            f = Fernet(self._key)
            return f.encrypt(plaintext.encode()).decode()

        # Dev fallback: salt + AES-256-CBC-like via HMAC + XOR (NOT for production)
        salt = secrets.token_bytes(16)
        key = self._derive_key(salt)
        data = plaintext.encode()
        # Simple deterministic obfuscation for dev only
        ciphertext = bytes(a ^ b for a, b in zip(data, key[:len(data)]))
        mac = hmac.new(key, salt + ciphertext, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(salt + ciphertext + mac).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64-encoded ciphertext. Returns plaintext."""
        if not ciphertext:
            return ""
        if _HAS_CRYPTOGRAPHY:
            f = Fernet(self._key)
            return f.decrypt(ciphertext.encode()).decode()

        # Dev fallback
        raw = base64.urlsafe_b64decode(ciphertext.encode())
        salt, encrypted, mac = raw[:16], raw[16:-32], raw[-32:]
        key = self._derive_key(salt)
        expected_mac = hmac.new(key, salt + encrypted, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("MAC verification failed — data tampered")
        plaintext = bytes(a ^ b for a, b in zip(encrypted, key[:len(encrypted)]))
        return plaintext.decode()

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone for logging: +23481****1111."""
        if not phone or len(phone) < 8:
            return "****"
        return phone[:4] + "****" + phone[-4:]

    @staticmethod
    def mask_id_number(id_number: str) -> str:
        """Mask ID for logging: NIN-****-5678."""
        if not id_number or len(id_number) < 4:
            return "****"
        return id_number[:4] + "****" + id_number[-4:]
