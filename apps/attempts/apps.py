from django.apps import AppConfig


class AttemptsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attempts"
    verbose_name = "Exam Attempts"

    def ready(self):
        import apps.attempts.signals  # noqa: F401
