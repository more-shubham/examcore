from django.db import models


class Question(models.Model):
    """MCQ Question for the question bank."""

    class Option(models.TextChoices):
        A = "A", "Option A"
        B = "B", "Option B"
        C = "C", "Option C"
        D = "D", "Option D"

    # Core fields
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=Option.choices)

    # Relations
    assigned_class = models.ForeignKey(
        "accounts.Class",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="questions_created",
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions"
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.question_text[:50]}... ({self.assigned_class.name})"

    def get_correct_answer_text(self):
        """Return the text of the correct option."""
        return getattr(self, f"option_{self.correct_option.lower()}")
