"""Custom managers for the Question model."""

from django.db import models


class QuestionQuerySet(models.QuerySet):
    """Custom QuerySet for Question model with common filters."""

    def active(self):
        """Filter to active questions only."""
        return self.filter(is_active=True)

    def for_subject(self, subject):
        """Filter to questions for a specific subject."""
        return self.filter(subject=subject)

    def active_for_subject(self, subject):
        """Filter to active questions for a specific subject."""
        return self.active().for_subject(subject)

    def by_creator(self, user):
        """Filter to questions created by a specific user."""
        return self.filter(created_by=user)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.select_related(
            "subject",
            "subject__assigned_class",
            "created_by",
            "correct_option",
        ).prefetch_related("options")

    def for_list_view(self):
        """Optimized queryset for list views."""
        return self.active().with_relations()


class QuestionManager(models.Manager):
    """Custom manager for Question model that uses QuestionQuerySet."""

    def get_queryset(self):
        """Return QuestionQuerySet instead of default QuerySet."""
        return QuestionQuerySet(self.model, using=self._db)

    def active(self):
        """Filter to active questions only."""
        return self.get_queryset().active()

    def for_subject(self, subject):
        """Filter to questions for a specific subject."""
        return self.get_queryset().for_subject(subject)

    def active_for_subject(self, subject):
        """Filter to active questions for a specific subject."""
        return self.get_queryset().active_for_subject(subject)

    def by_creator(self, user):
        """Filter to questions created by a specific user."""
        return self.get_queryset().by_creator(user)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.get_queryset().with_relations()

    def for_list_view(self):
        """Optimized queryset for list views."""
        return self.get_queryset().for_list_view()
