#!/bin/bash
# ============================================
# WHITENOISE STATIC FILES FIX
# Abia Migration Observatory — NASA-Level
# ============================================

cd ~/abia-migration-observatory/abia-app
source ../.venv/bin/activate

echo "[1/5] Installing WhiteNoise..."
pip install "whitenoise>=6.6"

echo ""
echo "[2/5] Patching settings.py..."

# Check if WhiteNoise is already in MIDDLEWARE
if ! grep -q "whitenoise" abia/settings.py; then
    # Insert WhiteNoise after SecurityMiddleware
    sed -i "/'django.middleware.security.SecurityMiddleware',/a\    'whitenoise.middleware.WhiteNoiseMiddleware'," abia/settings.py
    echo "  ✓ Added WhiteNoiseMiddleware to MIDDLEWARE"
else
    echo "  ℹ WhiteNoise already in MIDDLEWARE"
fi

# Add STATIC_ROOT if missing
if ! grep -q "STATIC_ROOT" abia/settings.py; then
    echo "" >> abia/settings.py
    echo "# Static files configuration" >> abia/settings.py
    echo "STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')" >> abia/settings.py
    echo "  ✓ Added STATIC_ROOT"
else
    echo "  ℹ STATIC_ROOT already set"
fi

# Add WhiteNoise storage if missing
if ! grep -q "CompressedManifestStaticFilesStorage" abia/settings.py; then
    echo "STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'" >> abia/settings.py
    echo "  ✓ Added WhiteNoise storage backend"
else
    echo "  ℹ Storage backend already set"
fi

echo ""
echo "[3/5] Creating static directories..."
mkdir -p static
mkdir -p staticfiles

echo ""
echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo ""
echo "[5/5] Verifying static files..."
if [ -f "staticfiles/admin/css/base.css" ]; then
    echo "  ✓ Admin CSS collected"
else
    echo "  ⚠ Admin CSS not found — checking..."
fi

if [ -f "staticfiles/admin/js/vendor/jquery/jquery.js" ]; then
    echo "  ✓ Admin JS collected"
else
    echo "  ⚠ Admin JS not found"
fi

echo ""
echo "=========================================="
echo "  WHITENOISE FIX COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Stop Gunicorn (Ctrl+C in server terminal)"
echo "  2. Restart: gunicorn abia.wsgi:application --bind 0.0.0.0:8002 --workers 2"
echo "  3. Visit: http://localhost:8002/admin/"
echo ""
echo "Static files will now be served automatically by WhiteNoise."
