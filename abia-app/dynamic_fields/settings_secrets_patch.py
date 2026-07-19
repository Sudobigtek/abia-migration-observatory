"""Patch settings to read Docker secrets."""
import os

def read_secret_file(path):
    """Read Docker secret from file."""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def patch_settings():
    """Apply secret patches to Django settings."""
    pass
