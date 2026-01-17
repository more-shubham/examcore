from django.conf import settings
from django.db import models
from django.utils import timezone

from .managers import ExamManager


class Exam(models.Model):
    """Exam definition created by Admin/Examiner."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    # Core fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Subject assignment
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        related_name="exams",
    )

    # Timing (simple: just start and end)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Question selection mode
    use_random_questions = models.BooleanField(default=True)
    random_question_count = models.PositiveIntegerField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exams_created",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExamManager()

    class Meta:
        db_table = "exams"
        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["is_active"], name="exams_active_idx"),
            models.Index(
                fields=["subject", "is_active"], name="exams_subject_active_idx"
            ),
            models.Index(
                fields=["status", "is_active"], name="exams_status_active_idx"
            ),
            models.Index(
                fields=["start_time", "end_time"], name="exams_time_range_idx"
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

    @property
    def duration_minutes(self):
        """Auto-calculate duration from start/end times."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)

    @property
    def duration_display(self):
        """Return human-readable duration."""
        minutes = self.duration_minutes
        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            if mins:
                return f"{hours}h {mins}m"
            return f"{hours}h"
        return f"{minutes}m"

    @property
    def is_upcoming(self):
        """Check if exam hasn't started yet."""
        return timezone.now() < self.start_time

    @property
    def is_running(self):
        """Check if exam is currently active."""
        now = timezone.now()
        return (
            self.start_time <= now <= self.end_time
            and self.status == self.Status.PUBLISHED
        )

    @property
    def is_ended(self):
        """Check if exam has ended."""
        return timezone.now() > self.end_time

    @property
    def status_display(self):
        """Return current exam status for display."""
        if self.status == self.Status.DRAFT:
            return "Draft"
        if self.is_upcoming:
            return "Upcoming"
        if self.is_running:
            return "Running"
        return "Ended"

    def get_questions(self):
        """
        Get questions for this exam.

        If using random questions, returns random selection from subject bank.
        If using manual selection, returns assigned questions.
        """
        if self.use_random_questions:
            from apps.questions.models import Question

            return Question.get_random_questions(
                self.subject, self.random_question_count or 10
            )
        return [eq.question for eq in self.exam_questions.select_related("question")]

    def get_question_count(self):
        """Return the number of questions in this exam."""
        if self.use_random_questions:
            return self.random_question_count or 0
        return self.exam_questions.count()


class ExamQuestion(models.Model):
    """Questions assigned to exam (for manual selection mode)."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="exam_questions",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
        related_name="exam_assignments",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "exam_questions"
        verbose_name = "Exam Question"
        verbose_name_plural = "Exam Questions"
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "question"], name="unique_question_per_exam"
            ),
        ]
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order + 1}"
