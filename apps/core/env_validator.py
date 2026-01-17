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
        self._validate_production_security()

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

    def _validate_production_security(self):
        """Validate security settings for production (DEBUG=False)."""
        if settings.DEBUG:
            # Skip production security checks in debug mode
            return

        # Check SSL redirect
        if not getattr(settings, "SECURE_SSL_REDIRECT", False):
            self.warnings.append(
                "SECURE_SSL_REDIRECT is False - HTTPS not enforced. "
                "Set to True unless behind a proxy that handles SSL."
            )

        # Check secure cookies
        if not getattr(settings, "SESSION_COOKIE_SECURE", False):
            self.errors.append("SESSION_COOKIE_SECURE must be True in production")

        if not getattr(settings, "CSRF_COOKIE_SECURE", False):
            self.errors.append("CSRF_COOKIE_SECURE must be True in production")

        # Check CSRF trusted origins
        csrf_origins = getattr(settings, "CSRF_TRUSTED_ORIGINS", [])
        if not csrf_origins:
            self.errors.append("CSRF_TRUSTED_ORIGINS must be configured in production")
        else:
            # Warn if any origins don't use HTTPS
            for origin in csrf_origins:
                if origin.startswith("http://"):
                    self.warnings.append(
                        f"CSRF_TRUSTED_ORIGINS contains non-HTTPS origin: {origin}"
                    )

        # Check HSTS settings
        hsts_seconds = getattr(settings, "SECURE_HSTS_SECONDS", 0)
        if hsts_seconds == 0:
            self.warnings.append(
                "SECURE_HSTS_SECONDS is 0 - HSTS not enabled. "
                "Consider setting to 31536000 (1 year) for production."
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
