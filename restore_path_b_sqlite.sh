#!/usr/bin/env bash
# ============================================================
# PATH B: SQLite + SpatiaLite Restoration
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

PROJECT_DIR="/home/abia/abia-migration-observatory"
APP_DIR="$PROJECT_DIR/abia-app"
SETTINGS="$APP_DIR/abia/settings.py"

echo -e "${BLUE}===============================================================${NC}"
echo -e "${BLUE}  PATH B: RESTORE SQLite + SpatiaLite${NC}"
echo -e "${BLUE}===============================================================${NC}"

cd "$PROJECT_DIR"

# Step 1: System libs
echo -e "${YELLOW}[1/6] Installing SpatiaLite system libraries...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq libsqlite3-mod-spatialite libspatialite-dev gdal-bin libgdal-dev || true
echo "  ✓ SpatiaLite libraries installed"

# Step 2: settings.py
echo -e "${YELLOW}[2/6] Restoring settings.py with SpatiaLite config...${NC}"
if [ -f "$SETTINGS" ]; then
    cp "$SETTINGS" "$SETTINGS.backup.$(date +%s)"
    echo "  ✓ Backed up existing settings.py"
fi

cat > "$SETTINGS" << 'SETTINSEOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-restore-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'corsheaders',
    'abia.accounts',
    'abia.migrants',
    'abia.observatory',
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
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'abia.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache://'
SETTINSEOF
echo "  ✓ settings.py restored with SpatiaLite"

# Step 3: requirements.txt
echo -e "${YELLOW}[3/6] Restoring requirements.txt...${NC}"
cat > "$PROJECT_DIR/requirements.txt" << 'REQEOF'
Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
Pillow>=10.0.0
celery>=5.3.0
python-dotenv>=1.0.0
gunicorn>=21.2.0
whitenoise>=6.6.0
REQEOF
echo "  ✓ requirements.txt restored (no psycopg2)"

# Step 4: Install deps
echo -e "${YELLOW}[4/6] Installing Python dependencies...${NC}"
if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
else
    echo -e "${YELLOW}  Creating virtual environment...${NC}"
    python3 -m venv "$PROJECT_DIR/.venv"
    source "$PROJECT_DIR/.venv/bin/activate"
fi
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"
echo "  ✓ Dependencies installed"

# Step 5: Init SpatiaLite
echo -e "${YELLOW}[5/6] Initializing SpatiaLite extension...${NC}"
python3 -c "
import sqlite3
conn = sqlite3.connect('$APP_DIR/db.sqlite3')
conn.enable_load_extension(True)
try:
    conn.load_extension('mod_spatialite')
except Exception as e:
    print('mod_spatialite load failed, trying spatialite:', e)
    conn.load_extension('spatialite')
conn.execute('SELECT InitSpatialMetaData();')
conn.close()
print('SpatiaLite initialized successfully')
" 2>/dev/null || echo "  ⚠ SpatiaLite init may be handled by Django migrations"

# Step 6: Migrations
echo -e "${YELLOW}[6/6] Running Django migrations...${NC}"
cd "$APP_DIR"
python manage.py migrate
echo "  ✓ Migrations complete"

echo ""
echo -e "${GREEN}===============================================================${NC}"
echo -e "${GREEN}  PATH B RESTORATION COMPLETE${NC}"
echo -e "${GREEN}===============================================================${NC}"
echo ""
echo "  Start the server:"
echo "    cd $APP_DIR"
echo "    python manage.py runserver"
echo ""
echo -e "${YELLOW}  NOTE:${NC} SQLite is single-user. Celery runs synchronously."
echo "        Switch to Path A (Docker+PostGIS) for production."
echo ""
