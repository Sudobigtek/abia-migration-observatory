from django.apps import AppConfig


class CasesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abia.cases"

    def ready(self):
        import abia.cases.signals  # noqa
