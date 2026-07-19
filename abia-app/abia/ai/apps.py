from django.apps import AppConfig

class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'abia.ai'
    verbose_name = 'AI & Predictive Analytics'

    def ready(self):
        import abia.ai.signals
