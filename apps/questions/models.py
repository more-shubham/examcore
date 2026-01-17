import secrets

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel

from .managers import QuestionManager


class QuestionOption(TimestampedModel):
    """Individual option for a question."""

    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=500)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="question_options_updated",
    )

    class Meta:
        db_table = "question_options"
        verbose_name = "Question Option"
        verbose_name_plural = "Question Options"

    def __str__(self):
        return self.text[:50]


class Question(TimestampedModel):
    """MCQ Question for the question bank."""

    # Core fields
    question_text = models.TextField()
    correct_option = models.ForeignKey(
        "QuestionOption",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="correct_for_questions",
    )

    # Relations
    subject = models.ForeignKey(
        "academic.Subject",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questions_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions_updated",
    )

    # Metadata
    is_active = models.BooleanField(default=True)

    objects = QuestionManager()

    class Meta:
        db_table = "questions"
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"], name="questions_active_idx"),
            models.Index(
                fields=["subject", "is_active"], name="questions_subject_active_idx"
            ),
        ]

    def __str__(self):
        return f"{self.question_text[:50]}... ({self.subject.name})"

    def get_correct_answer_text(self):
        """Return the text of the correct option."""
        if self.correct_option:
            return self.correct_option.text
        return ""

    def get_options_list(self):
        """Return all options as a list of QuestionOption objects."""
        return list(self.options.all())

    def get_shuffled_options(self):
        """
        Return shuffled options for exam display.

        Returns a list of dicts with:
        - 'label': Display label (1, 2, 3, ...)
        - 'text': Option text
        - 'option_id': The option's database ID
        - 'is_correct': Boolean indicating if this is the correct answer

        Using secrets module for cryptographically secure shuffling.
        """
        options = list(self.options.all())

        # Cryptographically secure shuffle using secrets
        shuffled = []
        temp_options = options.copy()
        while temp_options:
            index = secrets.randbelow(len(temp_options))
            shuffled.append(temp_options.pop(index))

        # Build result with new display labels (1, 2, 3, ...)
        result = []
        for i, option in enumerate(shuffled, start=1):
            result.append(
                {
                    "label": str(i),
                    "text": option.text,
                    "option_id": option.id,
                    "is_correct": (
                        self.correct_option_id == option.id
                        if self.correct_option_id
                        else False
                    ),
                }
            )

        return result

    @staticmethod
    def get_random_questions(subject, count):
        """
        Get random questions from a subject for exam generation.

        Args:
            subject: The Subject instance to get questions from
            count: Number of questions to select

        Returns:
            QuerySet of randomly selected questions
        """
        all_questions = list(Question.objects.filter(subject=subject, is_active=True))

        if len(all_questions) <= count:
            return all_questions

        # Cryptographically secure random selection
        selected = []
        temp_questions = all_questions.copy()
        for _ in range(count):
            if not temp_questions:
                break
            index = secrets.randbelow(len(temp_questions))
            selected.append(temp_questions.pop(index))

        return selected
