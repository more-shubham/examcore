from django.db import models


class ExamAttemptQuerySet(models.QuerySet):
    """Custom QuerySet for ExamAttempt model with common filters."""

    def in_progress(self):
        """Filter to in-progress attempts."""
        return self.filter(status=self.model.Status.IN_PROGRESS)

    def submitted(self):
        """Filter to submitted attempts."""
        return self.filter(status=self.model.Status.SUBMITTED)

    def timed_out(self):
        """Filter to timed-out attempts."""
        return self.filter(status=self.model.Status.TIMED_OUT)

    def completed(self):
        """Filter to completed attempts (submitted or timed out)."""
        return self.filter(
            status__in=[self.model.Status.SUBMITTED, self.model.Status.TIMED_OUT]
        )

    def for_student(self, student):
        """Filter to attempts by a specific student."""
        return self.filter(student=student)

    def for_exam(self, exam):
        """Filter to attempts for a specific exam."""
        return self.filter(exam=exam)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.select_related(
            "exam",
            "exam__subject",
            "exam__subject__assigned_class",
            "student",
        )

    def with_answers(self):
        """Include answers with related objects."""
        return self.prefetch_related(
            "answers",
            "answers__question",
            "answers__selected_option",
        )

    def for_result_view(self):
        """Optimized queryset for result views."""
        return self.with_relations().with_answers()


class ExamAttemptManager(models.Manager):
    """Custom manager for ExamAttempt model that uses ExamAttemptQuerySet."""

    def get_queryset(self):
        """Return ExamAttemptQuerySet instead of default QuerySet."""
        return ExamAttemptQuerySet(self.model, using=self._db)

    def in_progress(self):
        """Filter to in-progress attempts."""
        return self.get_queryset().in_progress()

    def submitted(self):
        """Filter to submitted attempts."""
        return self.get_queryset().submitted()

    def timed_out(self):
        """Filter to timed-out attempts."""
        return self.get_queryset().timed_out()

    def completed(self):
        """Filter to completed attempts."""
        return self.get_queryset().completed()

    def for_student(self, student):
        """Filter to attempts by a specific student."""
        return self.get_queryset().for_student(student)

    def for_exam(self, exam):
        """Filter to attempts for a specific exam."""
        return self.get_queryset().for_exam(exam)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.get_queryset().with_relations()

    def with_answers(self):
        """Include answers with related objects."""
        return self.get_queryset().with_answers()

    def for_result_view(self):
        """Optimized queryset for result views."""
        return self.get_queryset().for_result_view()


class ExamAnswerQuerySet(models.QuerySet):
    """Custom QuerySet for ExamAnswer model with common filters."""

    def correct(self):
        """Filter to correct answers."""
        return self.filter(is_correct=True)

    def incorrect(self):
        """Filter to incorrect answers."""
        return self.filter(is_correct=False)

    def for_attempt(self, attempt):
        """Filter to answers for a specific attempt."""
        return self.filter(attempt=attempt)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.select_related(
            "question",
            "selected_option",
        )


class ExamAnswerManager(models.Manager):
    """Custom manager for ExamAnswer model that uses ExamAnswerQuerySet."""

    def get_queryset(self):
        """Return ExamAnswerQuerySet instead of default QuerySet."""
        return ExamAnswerQuerySet(self.model, using=self._db)

    def correct(self):
        """Filter to correct answers."""
        return self.get_queryset().correct()

    def incorrect(self):
        """Filter to incorrect answers."""
        return self.get_queryset().incorrect()

    def for_attempt(self, attempt):
        """Filter to answers for a specific attempt."""
        return self.get_queryset().for_attempt(attempt)

    def with_relations(self):
        """Include related objects to avoid N+1 queries."""
        return self.get_queryset().with_relations()
