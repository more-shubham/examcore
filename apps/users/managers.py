"""Custom managers for the User model."""

from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models


class UserQuerySet(models.QuerySet):
    """Custom QuerySet for User model with common filters."""

    def active(self):
        """Filter to active users only."""
        return self.filter(is_active=True)

    def admins(self):
        """Filter to admin users."""
        return self.filter(role="admin")

    def examiners(self):
        """Filter to examiner users."""
        return self.filter(role="examiner")

    def teachers(self):
        """Filter to teacher users."""
        return self.filter(role="teacher")

    def students(self):
        """Filter to student users."""
        return self.filter(role="student")

    def in_class(self, assigned_class):
        """Filter to users in a specific class."""
        return self.filter(assigned_class=assigned_class)

    def active_students(self):
        """Filter to active student users."""
        return self.active().students()

    def active_in_class(self, assigned_class):
        """Filter to active users in a specific class."""
        return self.active().in_class(assigned_class)


class UserManager(BaseUserManager):
    """Custom manager for User model that uses UserQuerySet."""

    def get_queryset(self):
        """Return UserQuerySet instead of default QuerySet."""
        return UserQuerySet(self.model, using=self._db)

    def active(self):
        """Filter to active users only."""
        return self.get_queryset().active()

    def admins(self):
        """Filter to admin users."""
        return self.get_queryset().admins()

    def examiners(self):
        """Filter to examiner users."""
        return self.get_queryset().examiners()

    def teachers(self):
        """Filter to teacher users."""
        return self.get_queryset().teachers()

    def students(self):
        """Filter to student users."""
        return self.get_queryset().students()

    def in_class(self, assigned_class):
        """Filter to users in a specific class."""
        return self.get_queryset().in_class(assigned_class)

    def active_students(self):
        """Filter to active student users."""
        return self.get_queryset().active_students()

    def active_in_class(self, assigned_class):
        """Filter to active users in a specific class."""
        return self.get_queryset().active_in_class(assigned_class)
