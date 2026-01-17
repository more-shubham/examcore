"""
Environment validation module.
Validates required environment variables at Django startup.
"""

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Validates environment configuration at startup."""

    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validations and raise if critical errors found."""
        self._validate_secret_key()
        self._validate_debug_mode()
        self._validate_allowed_hosts()
        self._validate_database()
        self._validate_email()
        self._validate_logging()

        # Log warnings
        for warning in self.warnings:
            logger.warning(f"[ENV] {warning}")

        # Raise on errors
        if self.errors:
            error_msg = "Environment validation failed:\n" + "\n".join(
                f"  - {e}" for e in self.errors
            )
            raise ImproperlyConfigured(error_msg)

        logger.info("[ENV] Environment validation passed")

    def _validate_secret_key(self):
        key = settings.SECRET_KEY
        if not key:
            self.errors.append("SECRET_KEY is required")
        elif len(key) < 50:
            self.errors.append("SECRET_KEY must be at least 50 characters")
        elif "insecure" in key.lower() or key.startswith("django-insecure"):
            self.errors.append("SECRET_KEY contains insecure default value")

    def _validate_debug_mode(self):
        if settings.DEBUG:
            self.warnings.append("DEBUG is True - ensure this is intentional")

    def _validate_allowed_hosts(self):
        if not settings.ALLOWED_HOSTS:
            self.errors.append("ALLOWED_HOSTS must be configured")

    def _validate_database(self):
        db = settings.DATABASES.get("default", {})
        if not db.get("NAME"):
            self.errors.append("Database NAME (POSTGRES_DB) is required")
        if not db.get("USER"):
            self.errors.append("Database USER (POSTGRES_USER) is required")
        if not db.get("PASSWORD"):
            self.errors.append("Database PASSWORD (POSTGRES_PASSWORD) is required")
        elif db.get("PASSWORD") == "examcore123":
            # Warn in development, error in production
            if settings.DEBUG:
                self.warnings.append(
                    "Database PASSWORD is using insecure default - change for production"
                )
            else:
                self.errors.append("Database PASSWORD is using insecure default")
        if not db.get("HOST"):
            self.errors.append("Database HOST (DB_HOST) is required")

    def _validate_email(self):
        if not settings.EMAIL_HOST:
            self.errors.append("EMAIL_HOST is required")
        port = settings.EMAIL_PORT
        if not (1 <= port <= 65535):
            self.errors.append(f"EMAIL_PORT must be 1-65535, got: {port}")

    def _validate_logging(self):
        log_level = getattr(settings, "LOG_LEVEL", "INFO")
        if log_level.upper() not in self.VALID_LOG_LEVELS:
            self.errors.append(
                f"LOG_LEVEL must be one of {self.VALID_LOG_LEVELS}, got: {log_level}"
            )


# Module-level flag to prevent duplicate validation
_validated = False


def validate_environment():
    """Run environment validation (only once)."""
    global _validated
    if _validated:
        return
    _validated = True

    validator = EnvironmentValidator()
    validator.validate()
