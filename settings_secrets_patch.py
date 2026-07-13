"""
# Add to abia/settings.py — replace hardcoded PASSWORD with file-based secret reading

import os

def read_secret_file(path):
    """Read Docker secret from file."""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# Database password from Docker secret or env fallback
DB_PASSWORD = read_secret_file('/run/secrets/postgres_password') or os.environ.get('POSTGRES_PASSWORD', 'postgres')

# Django secret key from Docker secret or env fallback
SECRET_KEY = read_secret_file('/run/secrets/django_secret_key') or os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key')

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB", "abia_app"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": DB_PASSWORD,
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
"""
