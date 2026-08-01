import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "abia.settings")
app = Celery("abia")
# NASA: Docker-aware broker config
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://abia-redis:6379/0')
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://abia-redis:6379/0')
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()