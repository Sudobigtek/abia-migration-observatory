from .base import *

DEBUG = True
ENVIRONMENT = 'development'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'abia',
        'USER': 'abia',
        'PASSWORD': 'abia',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
