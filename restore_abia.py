#!/usr/bin/env python3
"""
ABIA Migration Observatory — Self-Extracting Restoration Script
Run: python3 restore_abia.py
This creates all 5 restoration files in your project directory.
"""

import os
import textwrap

PROJECT_DIR = "/home/abia/abia-migration-observatory"
APP_DIR = os.path.join(PROJECT_DIR, "abia-app")
RESTORE_DIR = os.path.join(PROJECT_DIR, "restore_scripts")

os.makedirs(RESTORE_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# FILE 1: diagnose.sh
# ─────────────────────────────────────────────────────────────
diagnose_sh = r"""#!/usr/bin/env bash
# ============================================================
# ABIA MIGRATION OBSERVATORY — SYSTEM DIAGNOSTIC
# Run this FIRST to determine which restoration path to take.
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

PROJECT_DIR="/home/abia/abia-migration-observatory"
APP_DIR="$PROJECT_DIR/abia-app"
SETTINGS="$APP_DIR/abia/settings.py"

echo -e "${BLUE}===============================================================${NC}"
echo -e "${BLUE}  ABIA MIGRATION OBSERVATORY — DIAGNOSTIC REPORT${NC}"
echo -e "${BLUE}===============================================================${NC}"
echo ""

# 1. Python & venv
echo -e "${YELLOW}[1/7] Checking Python & Virtual Environment...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VER=$(python3 --version 2>&1)
    echo "  ✓ Python found: $PYTHON_VER"
else
    echo "  ✗ Python3 not found — CRITICAL"
fi

if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "  ✓ .venv directory exists"
else
    echo "  ✗ .venv directory missing"
fi

# 2. Docker
echo -e "${YELLOW}[2/7] Checking Docker...${NC}"
if command -v docker &>/dev/null; then
    DOCKER_VER=$(docker --version 2>&1)
    echo "  ✓ Docker found: $DOCKER_VER"
    if docker ps &>/dev/null; then
        echo "  ✓ Docker daemon is running"
    else
        echo "  ✗ Docker daemon not accessible (check WSL integration)"
    fi
else
    echo "  ✗ Docker not found in PATH"
fi

if command -v docker-compose &>/dev/null; then
    echo "  ✓ docker-compose found"
elif docker compose version &>/dev/null; then
    echo "  ✓ docker compose (plugin) found"
else
    echo "  ✗ Neither docker-compose nor docker compose found"
fi

# 3. PostgreSQL container
echo -e "${YELLOW}[3/7] Checking PostgreSQL/PostGIS containers...${NC}"
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'postgres\|postgis\|db'; then
    echo "  ✓ Database container is running"
    docker ps --format '     {{.Names}} ({{.Image}})' | grep -E 'postgres|postgis|db' || true
else
    echo "  ✗ No PostgreSQL/PostGIS container detected"
fi

# 4. Project structure
echo -e "${YELLOW}[4/7] Checking project structure...${NC}"
if [ -f "$SETTINGS" ]; then
    echo "  ✓ settings.py found"
else
    echo "  ✗ settings.py NOT found at expected path"
    echo "     Expected: $SETTINGS"
fi

if [ -f "$APP_DIR/manage.py" ]; then
    echo "  ✓ manage.py found"
else
    echo "  ✗ manage.py NOT found"
fi

# 5. Database engine
echo -e "${YELLOW}[5/7] Checking database engine in settings.py...${NC}"
if [ -f "$SETTINGS" ]; then
    if grep -q 'django.db.backends.postgresql' "$SETTINGS"; then
        echo "  ✓ PostgreSQL backend configured"
    elif grep -q 'django.db.backends.sqlite3' "$SETTINGS"; then
        echo "  ⚠ SQLite backend configured (GeoDjango fields may fail)"
    elif grep -q 'django.contrib.gis.db.backends.spatialite' "$SETTINGS"; then
        echo "  ✓ SpatiaLite backend configured"
    elif grep -q 'django.contrib.gis.db.backends.postgis' "$SETTINGS"; then
        echo "  ✓ PostGIS backend configured"
    else
        echo "  ? Unknown database backend"
    fi
else
    echo "  ✗ Cannot check — settings.py missing"
fi

# 6. GeoDjango fields
echo -e "${YELLOW}[6/7] Checking for GeoDjango spatial fields...${NC}"
if [ -d "$APP_DIR" ]; then
    GEO_FIELDS=$(grep -rE 'PointField|PolygonField|MultiPolygonField|LineStringField|GeometryField' "$APP_DIR" --include="*.py" 2>/dev/null | wc -l)
    if [ "$GEO_FIELDS" -gt 0 ]; then
        echo "  ✓ Found $GEO_FIELDS spatial field(s) — PostGIS or SpatiaLite REQUIRED"
    else
        echo "  ✓ No spatial fields found — standard database OK"
    fi
else
    echo "  ✗ Cannot scan — app directory missing"
fi

# 7. Installed packages
echo -e "${YELLOW}[7/7] Checking installed Python packages...${NC}"
if [ -f "$PROJECT_DIR/.venv/bin/pip" ]; then
    PIP="$PROJECT_DIR/.venv/bin/pip"
elif [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
    PIP="$PROJECT_DIR/.venv/bin/python -m pip"
else
    PIP="python3 -m pip"
fi

$PIP list 2>/dev/null | grep -i django && echo "  ✓ Django installed" || echo "  ✗ Django NOT installed"
$PIP list 2>/dev/null | grep -i psycopg2 && echo "  ✓ psycopg2 installed" || echo "  ⚠ psycopg2 NOT installed (needed for PostgreSQL)"
$PIP list 2>/dev/null | grep -i gdal && echo "  ✓ GDAL installed" || echo "  ⚠ GDAL NOT installed (needed for GeoDjango)"

echo ""
echo -e "${BLUE}===============================================================${NC}"
echo -e "${BLUE}  RECOMMENDATION${NC}"
echo -e "${BLUE}===============================================================${NC}"

if command -v docker &>/dev/null && docker ps &>/dev/null; then
    echo -e "  → ${GREEN}PATH A (Docker + PostGIS)${NC} is available — run: bash restore_path_a_docker.sh"
else
    echo -e "  → ${YELLOW}PATH B (SQLite + SpatiaLite)${NC} is recommended — run: bash restore_path_b_sqlite.sh"
    echo "     Docker is not accessible. SpatiaLite gives you GeoDjango without Docker."
fi
echo ""
"""

# ─────────────────────────────────────────────────────────────
# FILE 2: restore_path_a_docker.sh
# ─────────────────────────────────────────────────────────────
restore_a_sh = r"""#!/usr/bin/env bash
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
"""

# ─────────────────────────────────────────────────────────────
# FILE 3: restore_path_b_sqlite.sh
# ─────────────────────────────────────────────────────────────
restore_b_sh = r"""#!/usr/bin/env bash
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
"""

# ─────────────────────────────────────────────────────────────
# FILE 4: urls_py_fix.py
# ─────────────────────────────────────────────────────────────
urls_fix_py = r"""#!/usr/bin/env python3
import os

URLS_FILE = "/home/abia/abia-migration-observatory/abia-app/abia/urls.py"

if not os.path.exists(URLS_FILE):
    print("ERROR: " + URLS_FILE + " not found")
    exit(1)

with open(URLS_FILE, 'r') as f:
    content = f.read()

if "from django.views.generic import TemplateView" not in content:
    content = "from django.views.generic import TemplateView
" + content
    print("Added TemplateView import")

landing_path = "    path('', TemplateView.as_view(template_name='landing.html'), name='home'),"
if "path('', TemplateView.as_view(template_name='landing.html')" not in content:
    content = content.replace(
        "urlpatterns = [",
        "urlpatterns = [
" + landing_path
    )
    print("Added landing page route")
else:
    print("Landing page route already exists")

with open(URLS_FILE, 'w') as f:
    f.write(content)

print("urls.py updated successfully")
"""

# ─────────────────────────────────────────────────────────────
# FILE 5: README.md
# ─────────────────────────────────────────────────────────────
readme_md = r"""# ABIA Migration Observatory — Restoration Package

## Quick Start (Choose ONE Path)

### Step 0: Diagnose (30 seconds)
```bash
cd /home/abia/abia-migration-observatory/restore_scripts
bash diagnose.sh
```

### Path A: Docker + PostGIS (Recommended)
```bash
bash restore_path_a_docker.sh
```

### Path B: SQLite + SpatiaLite (Fallback)
```bash
bash restore_path_b_sqlite.sh
```

### Post-Restoration: Wire Landing Page
```bash
python3 urls_py_fix.py
```

### Start the Server
```bash
cd /home/abia/abia-migration-observatory/abia-app
python manage.py runserver
```

## What Each Script Does

| Script | Purpose |
|--------|---------|
| diagnose.sh | Checks Python, venv, Docker, containers, DB engine, GeoDjango fields |
| restore_path_a_docker.sh | Full PostGIS restoration with Docker container startup |
| restore_path_b_sqlite.sh | SpatiaLite fallback with system library installation |
| urls_py_fix.py | Adds landing page route to abia/urls.py |

## Troubleshooting

- Docker not found in WSL: Enable WSL Integration in Docker Desktop → Settings → Resources → WSL Integration
- PostGIS container won't start: Check port 5432 is free (`sudo lsof -i :5432`)
- SpatiaLite load fails: Run `sudo apt-get install libsqlite3-mod-spatialite`
- Migrations fail: Delete `db.sqlite3` and `__pycache__` folders, then re-run
"""

# ─────────────────────────────────────────────────────────────
# WRITE ALL FILES
# ─────────────────────────────────────────────────────────────
files = {
    "diagnose.sh": diagnose_sh,
    "restore_path_a_docker.sh": restore_a_sh,
    "restore_path_b_sqlite.sh": restore_b_sh,
    "urls_py_fix.py": urls_fix_py,
    "README.md": readme_md,
}

print("=" * 65)
print("  ABIA MIGRATION OBSERVATORY — RESTORATION FILE CREATOR")
print("=" * 65)
print()

for filename, content in files.items():
    filepath = os.path.join(RESTORE_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    if filename.endswith('.sh'):
        os.chmod(filepath, 0o755)
    print(f"  ✓ Created: {filepath}")

# Also copy to project root for convenience
for filename in files:
    src = os.path.join(RESTORE_DIR, filename)
    dst = os.path.join(PROJECT_DIR, filename)
    with open(src, 'r') as f:
        content = f.read()
    with open(dst, 'w') as f:
        f.write(content)
    if filename.endswith('.sh'):
        os.chmod(dst, 0o755)

print()
print("=" * 65)
print("  ALL FILES CREATED SUCCESSFULLY")
print("=" * 65)
print()
print(f"  Location: {RESTORE_DIR}/")
print()
print("  NEXT STEP:")
print(f"    cd {RESTORE_DIR}")
print("    bash diagnose.sh")
print()
