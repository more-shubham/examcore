"""
Development settings for ExamCore project.

Use this settings module for local development.
"""

from decouple import config

from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = True

# =============================================================================
# ALLOWED HOSTS
# =============================================================================

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # nosec B104


# =============================================================================
# DATABASE (SQLite for quick development)
# =============================================================================

# Uncomment to use SQLite instead of PostgreSQL for quick local development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
#     }
# }

# =============================================================================
# EMAIL (Console backend for development)
# =============================================================================

# Use console backend to see emails in terminal
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Or use Mailpit (configure in docker-compose)
# EMAIL_HOST defaults to "localhost" for local dev, or "mailpit" when running in Docker
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=1025, cast=int)

# =============================================================================
# CACHING (Use database cache from base settings for consistency)
# =============================================================================

# Uses database cache from base.py - run: python manage.py createcachetable

# =============================================================================
# STATIC FILES (No compression in development)
# =============================================================================

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# =============================================================================
# LOGGING (More verbose in development)
# =============================================================================

LOGGING["handlers"]["console"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
