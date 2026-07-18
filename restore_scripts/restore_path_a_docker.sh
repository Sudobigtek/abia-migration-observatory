#!/usr/bin/env bash
# ============================================================
# PATH A: Docker + PostgreSQL/PostGIS Restoration
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

PROJECT_DIR="/home/abia/abia-migration-observatory"
APP_DIR="$PROJECT_DIR/abia-app"
SETTINGS="$APP_DIR/abia/settings.py"

echo -e "${BLUE}===============================================================${NC}"
echo -e "${BLUE}  PATH A: RESTORE Docker + PostgreSQL/PostGIS${NC}"
echo -e "${BLUE}===============================================================${NC}"

if command -v docker &>/dev/null; then
    DOCKER_CMD="docker"
elif command -v docker.exe &>/dev/null; then
    DOCKER_CMD="docker.exe"
    echo -e "${YELLOW}  Using docker.exe (Windows Docker Desktop)${NC}"
else
    echo -e "${RED}  ERROR: Docker not found. Run PATH B instead.${NC}"
    exit 1
fi

if $DOCKER_CMD compose version &>/dev/null; then
    COMPOSE_CMD="$DOCKER_CMD compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${YELLOW}  WARNING: docker-compose not found. Will start container manually.${NC}"
    COMPOSE_CMD=""
fi

cd "$PROJECT_DIR"

# Step 1: .env
echo -e "${YELLOW}[1/6] Creating .env file...${NC}"
cat > "$PROJECT_DIR/.env" << 'ENVEOF'
DEBUG=True
SECRET_KEY=django-insecure-restore-key-change-in-production
DATABASE_URL=postgis://postgres:postgres@localhost:5432/abia_migration_db
POSTGRES_DB=abia_migration_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
ENVEOF
echo "  ✓ .env created"

# Step 2: settings.py
echo -e "${YELLOW}[2/6] Restoring settings.py with PostGIS config...${NC}"
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

db_url = os.environ.get('DATABASE_URL', 'postgis://postgres:postgres@localhost:5432/abia_migration_db')
import urllib.parse
parsed = urllib.parse.urlparse(db_url)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': parsed.path.lstrip('/') or 'abia_migration_db',
        'USER': parsed.username or 'postgres',
        'PASSWORD': parsed.password or 'postgres',
        'HOST': parsed.hostname or 'localhost',
        'PORT': parsed.port or '5432',
    }
}

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

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
SETTINSEOF
echo "  ✓ settings.py restored with PostGIS"

# Step 3: requirements.txt
echo -e "${YELLOW}[3/6] Restoring requirements.txt...${NC}"
cat > "$PROJECT_DIR/requirements.txt" << 'REQEOF'
Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
psycopg2-binary>=2.9.9
Pillow>=10.0.0
celery>=5.3.0
redis>=5.0.0
python-dotenv>=1.0.0
gunicorn>=21.2.0
whitenoise>=6.6.0
REQEOF
echo "  ✓ requirements.txt restored"

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

# Step 5: Start PostGIS
echo -e "${YELLOW}[5/6] Starting PostGIS container...${NC}"
if [ -n "$COMPOSE_CMD" ] && [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
    $COMPOSE_CMD up -d db 2>/dev/null || true
fi

if ! $DOCKER_CMD ps --format '{{.Names}}' | grep -qE 'postgres|postgis|db'; then
    echo "  Starting PostGIS container directly..."
    $DOCKER_CMD run -d \
        --name abia-postgis \
        -e POSTGRES_DB=abia_migration_db \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -p 5432:5432 \
        --restart unless-stopped \
        postgis/postgis:15-3.4 2>/dev/null || \
    $DOCKER_CMD run -d \
        --name abia-postgis \
        -e POSTGRES_DB=abia_migration_db \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -p 5432:5432 \
        --restart unless-stopped \
        mdillon/postgis:latest 2>/dev/null || true
fi

sleep 5
for i in {1..10}; do
    if $DOCKER_CMD exec abia-postgis pg_isready -U postgres &>/dev/null; then
        echo "  ✓ PostGIS is ready"
        break
    fi
    echo "  Waiting for PostGIS... ($i/10)"
    sleep 3
done

# Step 6: Migrations
echo -e "${YELLOW}[6/6] Running Django migrations...${NC}"
cd "$APP_DIR"
python manage.py migrate
echo "  ✓ Migrations complete"

echo ""
echo -e "${GREEN}===============================================================${NC}"
echo -e "${GREEN}  PATH A RESTORATION COMPLETE${NC}"
echo -e "${GREEN}===============================================================${NC}"
echo ""
echo "  Start the server:"
echo "    cd $APP_DIR"
echo "    python manage.py runserver"
echo ""
