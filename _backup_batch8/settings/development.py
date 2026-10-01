from .base import *

DEBUG = True
ENVIRONMENT = 'development'
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'abia_migration',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Celery
CELERY_BROKER_URL = 'redis://localhost:6380/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6380/0'

# ============================================================
# Batch 7 — Force SQLite for local development (no GDAL needed)
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# Disable GeoDjango spatial backend for now
INSTALLED_APPS = [app for app in INSTALLED_APPS if "gis" not in app.lower()]
# ============================================================
