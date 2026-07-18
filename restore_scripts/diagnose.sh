#!/usr/bin/env bash
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
