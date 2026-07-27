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
    'abia.nbs',
    'django.contrib.gis',
    'django.contrib.postgres',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    'drf_spectacular',
    'corsheaders',
    'abia.accounts',
    'abia.ai',
    'abia.cases',
    'abia.ipfs',
    'abia.notifications',
 'abia.charts',
 'abia.importers',
 'abia.maps',
    'abia.migrants',
    'abia.referrals',
    'dynamic_fields',
    'abia.webhooks',
    'abia.push',
    'abia.geo',
    'abia.reports',
    'abia.throttle',
    'abia.quality',
    'abia.search',
    'abia.audit',
    'abia.pwa',
    'abia.tenant',
    'abia.ncfrmi',
    'abia.hotspot',
    'abia.workflows',
    'abia.documents',
    'abia.backup',
 'abia.iom',
 'abia.cbn',
 'abia.worldbank',
 'abia.wto',
 'abia.ecowas',
 'abia.sports',
 'abia.giz',
 'abia.ncfrmi_reporting',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'abia.common.middleware.APIVersionMiddleware',
    'abia.audit.middleware.AuditMiddleware',
    'abia.tenant.middleware.TenantMiddleware',
    'abia.common.middleware.PrometheusMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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

# PostGIS Database
db_url = os.environ.get('DATABASE_URL', 'postgis://postgres:postgres@localhost:5432/abia_migration_db')
import urllib.parse
parsed = urllib.parse.urlparse(db_url)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'abia'),
        'USER': os.getenv('DB_USER', 'abia'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'abia'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
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
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'memory://')
LOGIN_URL = '/admin/login/'

CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'memory://')

# Whitenoise static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# OpenAPI / Swagger Configuration
SPECTACULAR_SETTINGS = SPECTACULAR_SETTINGS = {
    'TITLE': 'Abia Migration Observatory API',
    'DESCRIPTION': 'API for subnational migration governance in Abia State, Nigeria',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'POSTPROCESSING_HOOKS': ['drf_spectacular.hooks.postprocess_schema_enums'],
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'TAGS': [
        {'name': 'Migrants', 'description': 'Migrant registry and management'},
        {'name': 'Cases', 'description': 'Case management and workflow'},
        {'name': 'Referrals', 'description': 'Service referrals and tracking'},
        {'name': 'Accounts', 'description': 'Users and LGA management'},
        {'name': 'AI', 'description': 'Risk assessment and predictive analytics'},
        {'name': 'IPFS', 'description': 'Document storage on IPFS'},
        {'name': 'Dynamic Fields', 'description': 'Custom field definitions and data'},
    ],
}

# Email Configuration (update for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@abia-migration.gov.ng'
# For production:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}

CACHE_TTL = 300

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'daily-backup': {
        'task': 'abia.backup_tasks.daily_backup',
        'schedule': 86400.0,
    },
    'weekly-cleanup': {
        'task': 'abia.backup_tasks.weekly_cleanup',
        'schedule': 604800.0,
    },
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# AllAuth / SSO Configuration
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'microsoft': {
        'APP': {
            'client_id': os.environ.get('MICROSOFT_CLIENT_ID', ''),
            'secret': os.environ.get('MICROSOFT_CLIENT_SECRET', ''),
            'key': ''
        },
        'SCOPE': ['openid', 'email', 'profile'],
    }
}
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "memory://",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = "default"

# CSRF trusted origins for Nginx proxy
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://abia-migration.gov.ng",
]
USE_X_FORWARDED_HOST = True

# HTTPSMS Configuration
HTTPSMS_API_KEY = os.environ.get("HTTPSMS_API_KEY", "")
HTTPSMS_SENDER_ID = os.environ.get("HTTPSMS_SENDER_ID", "AbiaObs")

# Celery Beat Schedule
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    "daily-digest": {
        "task": "abia.notifications.tasks.send_daily_digest",
        "schedule": crontab(hour=8, minute=0),
    },
}
