
from django.apps import AppConfig

class JapaDevelopmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abia.japa_development'
    label = 'japa_development'
    verbose_name = 'Japa for Development'

    def ready(self):
        import abia.japa_development.signals
