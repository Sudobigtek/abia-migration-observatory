from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abia.accounts"

    def ready(self):
        import abia.accounts.signals  # noqa
