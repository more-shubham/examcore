from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "authentication"  # Avoid conflict with django.contrib.auth
    verbose_name = "Authentication"
