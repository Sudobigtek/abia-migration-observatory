#!/usr/bin/env bash
# ============================================================
# Step 1: Git Commit & Push
# ============================================================
cd /home/abia/abia-migration-observatory

echo "=== Git Status ==="
git status --short

echo ""
echo "=== Staging essential files ==="
git add abia-app/abia/settings.py
# Check if files exist before adding
if [ -f "abia-app/abia/views.py" ]; then git add abia-app/abia/views.py; fi
git add requirements.txt

# Add new API files
for app in migrants cases referrals accounts; do
    for file in serializers.py views.py urls.py; do
        path="abia-app/abia/$app/$file"
        if [ -f "$path" ]; then git add "$path"; echo "  Staged: $path"; fi
    done
done

# Add templates
if [ -f "abia-app/templates/base.html" ]; then git add abia-app/templates/base.html; fi
if [ -f "abia-app/templates/dashboard.html" ]; then git add abia-app/templates/dashboard.html; fi

# Add filters
if [ -f "abia-app/abia/migrants/filters.py" ]; then git add abia-app/abia/migrants/filters.py; fi

echo ""
echo "=== Committing ==="
git commit -m "feat(api): Add Migrants, Cases, Referrals, Accounts APIs

- Add REST API with DRF for all core apps
- Add GeoJSON support via djangorestframework-gis
- Add dashboard with Chart.js, Leaflet maps
- Add workflow actions (assign, resolve, escalate, accept, reject, complete)
- Add permission hierarchy (field_officer -> super_admin)
- Add test data generator
- Configure PostGIS, AUTH_USER_MODEL, TokenAuthentication"

echo ""
echo "=== Pushing ==="
git push origin main

echo ""
echo "=== Done ==="
