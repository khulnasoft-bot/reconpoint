from django.apps import AppConfig


class ReconPointConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reconPoint"

    def ready(self):
        # Import signals here so they are registered when the app is ready
        import reconPoint.signals
