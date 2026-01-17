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

# CSRF trusted origins for development
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

# =============================================================================
# DATABASE
# =============================================================================

# Uses PostgreSQL from base.py by default
# Uncomment below to use SQLite for quick local development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
#     }
# }

# =============================================================================
# EMAIL
# =============================================================================

# Use Mailpit (configure in docker-compose) or console backend
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=1025, cast=int)

# =============================================================================
# CACHING
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
LOGGING["loggers"]["django.db.backends"]["level"] = "DEBUG"  # noqa: F405

# =============================================================================
# SECURITY (Relaxed for development)
# =============================================================================

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
