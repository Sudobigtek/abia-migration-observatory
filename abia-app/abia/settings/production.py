from .base import *

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
