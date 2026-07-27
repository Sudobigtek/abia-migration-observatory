import os
from .base import *

DEBUG = True
ENVIRONMENT = 'development'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Database: read all connection params from environment
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
