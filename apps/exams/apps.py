from django.apps import AppConfig


class ExamsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.exams"
    verbose_name = "Exams"

    def ready(self):
        import apps.exams.signals  # noqa: F401
