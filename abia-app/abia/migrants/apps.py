from django.apps import AppConfig


class MigrantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abia.migrants"

    def ready(self):
        import abia.migrants.signals  # noqa
