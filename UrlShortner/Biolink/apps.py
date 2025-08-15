from django.apps import AppConfig


class BiolinkConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Biolink"

    def ready(self):
        import Biolink.signals
