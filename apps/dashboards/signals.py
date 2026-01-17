"""Signal handlers for dashboard cache invalidation."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save

from .cache import invalidate_admin_dashboard_cache


def setup_cache_invalidation():
    """Set up signal handlers for cache invalidation."""
    from apps.academic.models import Class
    from apps.exams.models import Exam
    from apps.questions.models import Question

    User = get_user_model()

    # Connect signals for User model
    post_save.connect(invalidate_on_user_change, sender=User)
    post_delete.connect(invalidate_on_user_change, sender=User)

    # Connect signals for Exam model
    post_save.connect(invalidate_on_exam_change, sender=Exam)
    post_delete.connect(invalidate_on_exam_change, sender=Exam)

    # Connect signals for Question model
    post_save.connect(invalidate_on_question_change, sender=Question)
    post_delete.connect(invalidate_on_question_change, sender=Question)

    # Connect signals for Class model
    post_save.connect(invalidate_on_class_change, sender=Class)
    post_delete.connect(invalidate_on_class_change, sender=Class)


def invalidate_on_user_change(sender, instance, **kwargs):
    """Invalidate cache when user is created, updated, or deleted."""
    invalidate_admin_dashboard_cache()


def invalidate_on_exam_change(sender, instance, **kwargs):
    """Invalidate cache when exam is created, updated, or deleted."""
    invalidate_admin_dashboard_cache()


def invalidate_on_question_change(sender, instance, **kwargs):
    """Invalidate cache when question is created, updated, or deleted."""
    invalidate_admin_dashboard_cache()


def invalidate_on_class_change(sender, instance, **kwargs):
    """Invalidate cache when class is created, updated, or deleted."""
    invalidate_admin_dashboard_cache()
