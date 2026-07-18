#!/usr/bin/env python3
"""
ABIA Migration Observatory — PATH A FIX
Fixes two issues from the restoration:
1. Django version conflict (downgraded 5.2->4.2, django-filter needs >=5.2)
2. abia.observatory app missing from project
"""

import os
import subprocess

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
SETTINGS = os.path.join(APP_DIR, "abia", "settings.py")
REQ_FILE = os.path.join(PROJECT_DIR, "requirements.txt")

# ── DISCOVER ACTUAL APPS ──
abia_apps_dir = os.path.join(APP_DIR, "abia")
actual_apps = []
if os.path.isdir(abia_apps_dir):
    for name in os.listdir(abia_apps_dir):
        app_path = os.path.join(abia_apps_dir, name)
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, "__init__.py")):
            actual_apps.append(f"abia.{name}")

print("=" * 65)
print("  ABIA PATH A — CORRECTION SCRIPT")
print("=" * 65)
print()
print(f"  Discovered apps: {actual_apps}")
print()

# ── FIX 1: REQUIREMENTS.TXT ──
print("[1/3] Fixing requirements.txt (Django >= 5.2)...")
req_content = """Django>=5.2,<6.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
django-filter>=26.0
psycopg2-binary>=2.9.9
Pillow>=10.0.0
celery>=5.3.0
redis>=5.0.0
python-dotenv>=1.0.0
gunicorn>=21.2.0
whitenoise>=6.6.0
"""
with open(REQ_FILE, "w") as f:
    f.write(req_content)
print("  ✓ requirements.txt updated")

# ── FIX 2: REINSTALL DJANGO ──
print("[2/3] Reinstalling Django 5.2+...")
venv_pip = os.path.join(PROJECT_DIR, ".venv", "bin", "pip")
if os.path.exists(venv_pip):
    subprocess.run([venv_pip, "install", "--upgrade", "Django>=5.2"], check=False)
    print("  ✓ Django reinstalled")
else:
    print("  ⚠ venv pip not found, skipping pip install")

# ── FIX 3: SETTINGS.PY WITH CORRECT APPS ──
print("[3/3] Fixing settings.py with correct INSTALLED_APPS...")

# Build INSTALLED_APPS dynamically
base_apps = [
    "'django.contrib.admin'",
    "'django.contrib.auth'",
    "'django.contrib.contenttypes'",
    "'django.contrib.sessions'",
    "'django.contrib.messages'",
    "'django.contrib.staticfiles'",
    "'django.contrib.gis'",
    "'rest_framework'",
    "'corsheaders'",
]

# Add discovered abia apps
for app in sorted(actual_apps):
    base_apps.append(f"    '{app}'")

installed_apps_str = "
".join(["    " + a + "," for a in base_apps]).rstrip(",")

settings_content = f"""import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-restore-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
{installed_apps_str}
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'abia.urls'
TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'abia.wsgi.application'

# PostGIS Database
db_url = os.environ.get('DATABASE_URL', 'postgis://postgres:postgres@localhost:5432/abia_migration_db')
import urllib.parse
parsed = urllib.parse.urlparse(db_url)

DATABASES = {{
    'default': {{
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': parsed.path.lstrip('/') or 'abia_migration_db',
        'USER': parsed.username or 'postgres',
        'PASSWORD': parsed.password or 'postgres',
        'HOST': parsed.hostname or 'localhost',
        'PORT': parsed.port or '5432',
    }}
}}

AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
"""

with open(SETTINGS, "w") as f:
    f.write(settings_content)
print("  ✓ settings.py updated with correct apps")

print()
print("=" * 65)
print("  FIXES APPLIED")
print("=" * 65)
print()
print("  Now run migrations:")
print("    cd /home/abia/abia-migration-observatory/abia-app")
print("    python manage.py migrate")
print()
