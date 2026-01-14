import secrets

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
    subject = models.ForeignKey(
        "accounts.Subject",
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
        return f"{self.question_text[:50]}... ({self.subject.name})"

    def get_correct_answer_text(self):
        """Return the text of the correct option."""
        return getattr(self, f"option_{self.correct_option.lower()}")

    def get_options_list(self):
        """Return all options as a list of tuples (label, text)."""
        return [
            ("A", self.option_a),
            ("B", self.option_b),
            ("C", self.option_c),
            ("D", self.option_d),
        ]

    def get_shuffled_options(self):
        """
        Return shuffled options for exam display.

        Returns a list of dicts with:
        - 'label': Display label (1, 2, 3, 4)
        - 'text': Option text
        - 'original_key': Original option key (A, B, C, D)
        - 'is_correct': Boolean indicating if this is the correct answer

        Using secrets module for cryptographically secure shuffling.
        """
        options = self.get_options_list()

        # Cryptographically secure shuffle using secrets
        shuffled = []
        temp_options = options.copy()
        while temp_options:
            index = secrets.randbelow(len(temp_options))
            shuffled.append(temp_options.pop(index))

        # Build result with new display labels (1, 2, 3, 4)
        result = []
        for i, (original_key, text) in enumerate(shuffled, start=1):
            result.append(
                {
                    "label": str(i),
                    "text": text,
                    "original_key": original_key,
                    "is_correct": original_key == self.correct_option,
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
