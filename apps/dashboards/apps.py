from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboards"
    verbose_name = "Dashboards"

    def ready(self):
        """Set up signal handlers for cache invalidation."""
        from .signals import setup_cache_invalidation

        setup_cache_invalidation()
