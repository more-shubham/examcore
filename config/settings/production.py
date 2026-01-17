"""
Production settings for ExamCore project.

Use this settings module for production deployment.
"""

from decouple import config

from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG - Always False in production
# =============================================================================

DEBUG = False

# =============================================================================
# ALLOWED HOSTS - Required in production
# =============================================================================

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production")

# =============================================================================
# SECURITY - HTTPS and Cookie Settings
# =============================================================================

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

# Cookie security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# HSTS settings (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Other security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # Deprecated but doesn't hurt
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# Permissions Policy (formerly Feature Policy)
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# =============================================================================
# DATABASE - Production optimizations
# =============================================================================

DATABASES["default"]["CONN_MAX_AGE"] = config(  # noqa: F405
    "DB_CONN_MAX_AGE", default=600, cast=int  # 10 minutes for production
)

# Connection health checks
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405

# =============================================================================
# CACHING - Uses database cache from base.py
# =============================================================================

# Database cache is configured in base.py
# Run: python manage.py createcachetable

# =============================================================================
# SESSION - Database-backed sessions for production
# =============================================================================

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# =============================================================================
# EMAIL - Production SMTP settings
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_TIMEOUT = 30

# =============================================================================
# STATIC FILES - WhiteNoise for production
# =============================================================================

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# WhiteNoise settings
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files

# =============================================================================
# LOGGING - Production level
# =============================================================================

LOGGING["handlers"]["console"]["level"] = config(  # noqa: F405
    "LOG_LEVEL", default="WARNING"
)
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = config("LOG_LEVEL", default="INFO")  # noqa: F405

# =============================================================================
# ADMINS - Error notifications
# =============================================================================

_admin_email = config("ADMIN_EMAIL", default="")
if _admin_email:
    ADMINS = [("Admin", _admin_email)]
    MANAGERS = ADMINS

# =============================================================================
# PERFORMANCE - Template caching
# =============================================================================

# Cache templates in production
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa: F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    ),
]
# Remove APP_DIRS when using custom loaders
del TEMPLATES[0]["APP_DIRS"]  # noqa: F405

# =============================================================================
# FILE UPLOAD - Production limits
# =============================================================================

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
