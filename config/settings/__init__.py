"""
Settings package for ExamCore project.

By default, development settings are loaded.
Set DJANGO_SETTINGS_MODULE environment variable to change.

Available settings modules:
- config.settings.development (default)
- config.settings.production
- config.settings.test
"""

from .development import *  # noqa: F401, F403
