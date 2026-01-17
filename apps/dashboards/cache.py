"""Dashboard caching utilities for optimized query performance."""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Q

ADMIN_DASHBOARD_CACHE_KEY = "dashboard_admin_counts"
ADMIN_DASHBOARD_CACHE_TIMEOUT = 300  # 5 minutes


def get_admin_dashboard_counts():
    """
    Get admin dashboard counts with caching.

    Uses a single aggregation query for user counts instead of
    multiple separate COUNT queries, then caches the results.
    """
    counts = cache.get(ADMIN_DASHBOARD_CACHE_KEY)

    if counts is None:
        counts = _fetch_admin_dashboard_counts()
        cache.set(ADMIN_DASHBOARD_CACHE_KEY, counts, ADMIN_DASHBOARD_CACHE_TIMEOUT)

    return counts


def _fetch_admin_dashboard_counts():
    """Fetch dashboard counts using optimized queries."""
    from apps.academic.models import Class
    from apps.exams.models import Exam
    from apps.questions.models import Question

    User = get_user_model()

    # Single query for all user counts using conditional aggregation
    user_counts = User.objects.aggregate(
        examiner_count=Count("id", filter=Q(role=User.Role.EXAMINER, is_active=True)),
        teacher_count=Count("id", filter=Q(role=User.Role.TEACHER, is_active=True)),
        student_count=Count("id", filter=Q(role=User.Role.STUDENT, is_active=True)),
    )

    return {
        "question_count": Question.objects.filter(is_active=True).count(),
        "exam_count": Exam.objects.filter(is_active=True).count(),
        "class_count": Class.objects.filter(is_active=True).count(),
        **user_counts,
    }


def invalidate_admin_dashboard_cache():
    """Invalidate the admin dashboard cache."""
    cache.delete(ADMIN_DASHBOARD_CACHE_KEY)
