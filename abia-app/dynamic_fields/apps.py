from django.apps import AppConfig


class DynamicFieldsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dynamic_fields"
    verbose_name = "Dynamic Fields"

    def ready(self):
        import dynamic_fields.signals
