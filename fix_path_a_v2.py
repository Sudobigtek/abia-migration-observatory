#!/usr/bin/env python3
"""
ABIA Migration Observatory — PATH A FIX
Fixes Django version conflict and missing app issue.
"""

import os
import subprocess

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
SETTINGS = os.path.join(APP_DIR, "abia", "settings.py")
REQ_FILE = os.path.join(PROJECT_DIR, "requirements.txt")

# DISCOVER ACTUAL APPS
abia_apps_dir = os.path.join(APP_DIR, "abia")
actual_apps = []
if os.path.isdir(abia_apps_dir):
    for name in os.listdir(abia_apps_dir):
        app_path = os.path.join(abia_apps_dir, name)
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, "__init__.py")):
            actual_apps.append("abia." + name)

print("=" * 65)
print("  ABIA PATH A — CORRECTION SCRIPT")
print("=" * 65)
print()
print("  Discovered apps: " + str(actual_apps))
print()

# FIX 1: REQUIREMENTS.TXT
print("[1/3] Fixing requirements.txt (Django >= 5.2)...")
req_lines = [
    "Django>=5.2,<6.0",
    "djangorestframework>=3.14.0",
    "django-cors-headers>=4.3.0",
    "django-filter>=26.0",
    "psycopg2-binary>=2.9.9",
    "Pillow>=10.0.0",
    "celery>=5.3.0",
    "redis>=5.0.0",
    "python-dotenv>=1.0.0",
    "gunicorn>=21.2.0",
    "whitenoise>=6.6.0",
]
with open(REQ_FILE, "w") as f:
    f.write("\n".join(req_lines) + "\n")
print("  OK requirements.txt updated")

# FIX 2: REINSTALL DJANGO
print("[2/3] Reinstalling Django 5.2...")
venv_pip = os.path.join(PROJECT_DIR, ".venv", "bin", "pip")
if os.path.exists(venv_pip):
    subprocess.run([venv_pip, "install", "--upgrade", "Django>=5.2"], check=False)
    print("  OK Django reinstalled")
else:
    print("  WARN venv pip not found, skipping")

# FIX 3: SETTINGS.PY WITH CORRECT APPS
print("[3/3] Fixing settings.py with correct INSTALLED_APPS...")

base_apps = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "corsheaders",
]

all_apps = base_apps + sorted(actual_apps)

# Build INSTALLED_APPS string line by line
apps_lines = ["    '" + a + "'," for a in all_apps]
installed_apps_str = "\n".join(apps_lines)

# Build settings.py using simple string concatenation - NO triple quotes inside
parts = []
parts.append("import os")
parts.append("from pathlib import Path")
parts.append("")
parts.append("BASE_DIR = Path(__file__).resolve().parent.parent")
parts.append("")
parts.append("SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-restore-key-change-in-production')")
parts.append("DEBUG = os.environ.get('DEBUG', 'True') == 'True'")
parts.append("ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']")
parts.append("")
parts.append("INSTALLED_APPS = [")
parts.append(installed_apps_str)
parts.append("]")
parts.append("")
parts.append("MIDDLEWARE = [")
parts.append("    'corsheaders.middleware.CorsMiddleware',")
parts.append("    'django.middleware.security.SecurityMiddleware',")
parts.append("    'django.contrib.sessions.middleware.SessionMiddleware',")
parts.append("    'django.middleware.common.CommonMiddleware',")
parts.append("    'django.middleware.csrf.CsrfViewMiddleware',")
parts.append("    'django.contrib.auth.middleware.AuthenticationMiddleware',")
parts.append("    'django.contrib.messages.middleware.MessageMiddleware',")
parts.append("    'django.middleware.clickjacking.XFrameOptionsMiddleware',")
parts.append("]")
parts.append("")
parts.append("ROOT_URLCONF = 'abia.urls'")
parts.append("TEMPLATES = [")
parts.append("    {")
parts.append("        'BACKEND': 'django.template.backends.django.DjangoTemplates',")
parts.append("        'DIRS': [BASE_DIR / 'templates'],")
parts.append("        'APP_DIRS': True,")
parts.append("        'OPTIONS': {")
parts.append("            'context_processors': [")
parts.append("                'django.template.context_processors.debug',")
parts.append("                'django.template.context_processors.request',")
parts.append("                'django.contrib.auth.context_processors.auth',")
parts.append("                'django.contrib.messages.context_processors.messages',")
parts.append("            ],")
parts.append("        },")
parts.append("    },")
parts.append("]")
parts.append("")
parts.append("WSGI_APPLICATION = 'abia.wsgi.application'")
parts.append("")
parts.append("# PostGIS Database")
parts.append("db_url = os.environ.get('DATABASE_URL', 'postgis://postgres:postgres@localhost:5432/abia_migration_db')")
parts.append("import urllib.parse")
parts.append("parsed = urllib.parse.urlparse(db_url)")
parts.append("")
parts.append("DATABASES = {")
parts.append("    'default': {")
parts.append("        'ENGINE': 'django.contrib.gis.db.backends.postgis',")
parts.append("        'NAME': parsed.path.lstrip('/') or 'abia_migration_db',")
parts.append("        'USER': parsed.username or 'postgres',")
parts.append("        'PASSWORD': parsed.password or 'postgres',")
parts.append("        'HOST': parsed.hostname or 'localhost',")
parts.append("        'PORT': parsed.port or '5432',")
parts.append("    }")
parts.append("}")
parts.append("")
parts.append("AUTH_PASSWORD_VALIDATORS = [")
parts.append("    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},")
parts.append("    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},")
parts.append("    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},")
parts.append("    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},")
parts.append("]")
parts.append("")
parts.append("LANGUAGE_CODE = 'en-us'")
parts.append("TIME_ZONE = 'Africa/Lagos'")
parts.append("USE_I18N = True")
parts.append("USE_TZ = True")
parts.append("")
parts.append("STATIC_URL = '/static/'")
parts.append("STATIC_ROOT = BASE_DIR / 'staticfiles'")
parts.append("STATICFILES_DIRS = [BASE_DIR / 'static']")
parts.append("")
parts.append("MEDIA_URL = '/media/'")
parts.append("MEDIA_ROOT = BASE_DIR / 'media'")
parts.append("")
parts.append("DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'")
parts.append("")
parts.append("REST_FRAMEWORK = {")
parts.append("    'DEFAULT_AUTHENTICATION_CLASSES': [")
parts.append("        'rest_framework.authentication.SessionAuthentication',")
parts.append("    ],")
parts.append("    'DEFAULT_PERMISSION_CLASSES': [")
parts.append("        'rest_framework.permissions.IsAuthenticatedOrReadOnly',")
parts.append("    ],")
parts.append("}")
parts.append("")
parts.append("CORS_ALLOWED_ORIGINS = [")
parts.append('    "http://localhost:3000",')
parts.append('    "http://127.0.0.1:3000",')
parts.append("]")
parts.append("")
parts.append("CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')")
parts.append("CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')")
parts.append("")

settings_content = "\n".join(parts)

with open(SETTINGS, "w") as f:
    f.write(settings_content)
print("  OK settings.py updated with correct apps")

print()
print("=" * 65)
print("  FIXES APPLIED")
print("=" * 65)
print()
print("  Now run migrations:")
print("    cd /home/abia/abia-migration-observatory/abia-app")
print("    python manage.py migrate")
print()
