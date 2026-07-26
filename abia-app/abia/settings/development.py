from .base import *

DEBUG = True
ENVIRONMENT = 'development'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Development database (override with env vars if needed)
DATABASES['default']['HOST'] = os.getenv('DB_HOST', 'localhost')
