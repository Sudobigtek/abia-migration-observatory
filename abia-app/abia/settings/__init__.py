from .development import *

# NASA: Celery broker override for Docker/WSL compatibility
import os
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://abia-redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://abia-redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
