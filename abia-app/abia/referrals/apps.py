from django.apps import AppConfig


class ReferralsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "abia.referrals"

    def ready(self):
        import abia.referrals.signals  # noqa
