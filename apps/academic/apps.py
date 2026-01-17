from django.apps import AppConfig


class AcademicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.academic"
    verbose_name = "Academic"

    def ready(self):
        """Set up signal handlers for student count updates."""
        from .signals import setup_student_count_signals

        setup_student_count_signals()
