# ABIA Migration Observatory — Restoration Package

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
