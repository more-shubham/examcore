"""Custom managers for the Exam model."""

from django.db import models
from django.utils import timezone


class ExamQuerySet(models.QuerySet):
    """Custom QuerySet for Exam model with common filters."""

    def active(self):
        """Filter to active exams only."""
        return self.filter(is_active=True)

    def published(self):
        """Filter to published exams."""
        return self.filter(status="published")

    def draft(self):
        """Filter to draft exams."""
        return self.filter(status="draft")

    def for_subject(self, subject):
        """Filter to exams for a specific subject."""
        return self.filter(subject=subject)

    def for_class(self, assigned_class):
        """Filter to exams for a specific class."""
        return self.filter(subject__assigned_class=assigned_class)

    def by_creator(self, user):
        """Filter to exams created by a specific user."""
        return self.filter(created_by=user)

    def running(self):
        """Filter to currently running exams (within time window and published)."""
        now = timezone.now()
        return self.published().filter(
            start_time__lte=now,
            end_time__gte=now,
        )

    def upcoming(self):
        """Filter to upcoming exams (haven't started yet)."""
        now = timezone.now()
        return self.filter(start_time__gt=now)

    def ended(self):
        """Filter to ended exams."""
        now = timezone.now()
        return self.filter(end_time__lt=now)

    def available_for_student(self, student):
        """Filter to exams available for a specific student."""
        if not student.assigned_class:
            return self.none()
        return self.published().active().for_class(student.assigned_class)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.select_related(
            "subject",
            "subject__assigned_class",
            "created_by",
        )

    def for_list_view(self):
        """Optimized queryset for list views."""
        return self.active().with_relations()


class ExamManager(models.Manager):
    """Custom manager for Exam model that uses ExamQuerySet."""

    def get_queryset(self):
        """Return ExamQuerySet instead of default QuerySet."""
        return ExamQuerySet(self.model, using=self._db)

    def active(self):
        """Filter to active exams only."""
        return self.get_queryset().active()

    def published(self):
        """Filter to published exams."""
        return self.get_queryset().published()

    def draft(self):
        """Filter to draft exams."""
        return self.get_queryset().draft()

    def for_subject(self, subject):
        """Filter to exams for a specific subject."""
        return self.get_queryset().for_subject(subject)

    def for_class(self, assigned_class):
        """Filter to exams for a specific class."""
        return self.get_queryset().for_class(assigned_class)

    def by_creator(self, user):
        """Filter to exams created by a specific user."""
        return self.get_queryset().by_creator(user)

    def running(self):
        """Filter to currently running exams."""
        return self.get_queryset().running()

    def upcoming(self):
        """Filter to upcoming exams."""
        return self.get_queryset().upcoming()

    def ended(self):
        """Filter to ended exams."""
        return self.get_queryset().ended()

    def available_for_student(self, student):
        """Filter to exams available for a specific student."""
        return self.get_queryset().available_for_student(student)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.get_queryset().with_relations()

    def for_list_view(self):
        """Optimized queryset for list views."""
        return self.get_queryset().for_list_view()
