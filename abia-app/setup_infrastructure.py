import os
import shutil

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  CREATED:", p)

base_dir = "/home/abia/abia-migration-observatory/abia-app"
os.chdir(base_dir)

# =====================================================================
# 1. SCHEMA REGRESSION TEST
# =====================================================================
test_dir = "abia/common/tests"
os.makedirs(test_dir, exist_ok=True)

test_init = os.path.join(test_dir, "__init__.py")
if not os.path.exists(test_init):
    write(test_init, "")

test_file = os.path.join(test_dir, "test_schema.py")
if not os.path.exists(test_file):
    write(test_file, '''from django.test import TestCase
from django.core.management import call_command


class SchemaValidationTests(TestCase):
    def test_schema_generates_without_errors(self):
        """Fail the test if drf-spectacular produces errors."""
        call_command('spectacular', '--file', '/tmp/test_schema.yml', '--validate')
''')
    print("  [1/3] Schema regression test created.")
else:
    print("  [1/3] Schema test already exists. Skipping.")

# =====================================================================
# 2. SETTINGS SPLIT
# =====================================================================
settings_dir = "abia/settings"
settings_file = "abia/settings.py"

if os.path.exists(settings_file) and not os.path.exists(settings_dir):
    os.makedirs(settings_dir, exist_ok=True)
    
    # Move base settings
    shutil.move(settings_file, os.path.join(settings_dir, "base.py"))
    
    # Create __init__.py
    write(os.path.join(settings_dir, "__init__.py"), "from .base import *\n")
    
    # Create development.py
    dev_settings = '''from .base import *

DEBUG = True
ENVIRONMENT = 'development'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Development database (override with env vars if needed)
DATABASES['default']['HOST'] = os.getenv('DB_HOST', 'localhost')
'''
    write(os.path.join(settings_dir, "development.py"), dev_settings)
    
    # Create production.py
    prod_settings = '''from .base import *

DEBUG = False
ENVIRONMENT = 'production'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Security hardening
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Production database (env vars required)
DATABASES['default']['HOST'] = os.getenv('DB_HOST')
DATABASES['default']['NAME'] = os.getenv('DB_NAME')
DATABASES['default']['USER'] = os.getenv('DB_USER')
DATABASES['default']['PASSWORD'] = os.getenv('DB_PASSWORD')
'''
    write(os.path.join(settings_dir, "production.py"), prod_settings)
    
    # Update manage.py
    manage_file = "manage.py"
    if os.path.exists(manage_file):
        c = read(manage_file)
        c = c.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings.development')"
        )
        write(manage_file, c)
        print("  Updated manage.py")
    
    # Update wsgi.py
    wsgi_file = "abia/wsgi.py"
    if os.path.exists(wsgi_file):
        c = read(wsgi_file)
        c = c.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings.development')"
        )
        write(wsgi_file, c)
        print("  Updated wsgi.py")
    
    # Update asgi.py if it exists
    asgi_file = "abia/asgi.py"
    if os.path.exists(asgi_file):
        c = read(asgi_file)
        c = c.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings.development')"
        )
        write(asgi_file, c)
        print("  Updated asgi.py")
    
    print("  [2/3] Settings split complete.")
elif os.path.exists(settings_dir):
    print("  [2/3] Settings already split. Skipping.")
else:
    print("  [2/3] WARNING: abia/settings.py not found. Skipping split.")

# =====================================================================
# 3. DOCKER SETUP
# =====================================================================
dockerfile = '''FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for PostGIS and GDAL
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gdal-bin \\
    libgdal-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run development server (override in production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
'''

compose = '''version: "3.8"

services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: abia
      POSTGRES_USER: abia
      POSTGRES_PASSWORD: abia
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=abia.settings.development
      - DB_HOST=db
      - DB_NAME=abia
      - DB_USER=abia
      - DB_PASSWORD=abia
    depends_on:
      - db

volumes:
  postgres_data:
'''

env_example = '''DJANGO_SETTINGS_MODULE=abia.settings.development
DB_HOST=db
DB_NAME=abia
DB_USER=abia
DB_PASSWORD=abia
SECRET_KEY=change-me-in-production
DEBUG=True
ENVIRONMENT=development
'''

if not os.path.exists("Dockerfile"):
    write("Dockerfile", dockerfile)
if not os.path.exists("docker-compose.yml"):
    write("docker-compose.yml", compose)
if not os.path.exists(".env.example"):
    write(".env.example", env_example)
    print("  [3/3] Docker setup complete.")
else:
    print("  [3/3] Docker files already exist. Skipping.")

print("\n" + "="*60)
print("INFRASTRUCTURE SETUP COMPLETE")
print("="*60)
print("\nNext steps:")
print("  1. python3 manage.py check")
print("  2. python3 manage.py test abia.common.tests.test_schema")
print("  3. docker-compose up --build")
