import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimestampedModel


def secure_shuffle(items):
    """Cryptographically secure shuffle using secrets module."""
    items = list(items)
    for i in range(len(items) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]
    return items


class ExamAttempt(TimestampedModel):
    """Student's attempt at an exam with randomization data."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        TIMED_OUT = "timed_out", "Timed Out"

    exam = models.ForeignKey(
        "exams.Exam",
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_attempts",
    )
    question_order = models.JSONField(default=list)
    option_orders = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    score = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "exam_attempts"
        verbose_name = "Exam Attempt"
        verbose_name_plural = "Exam Attempts"
        unique_together = ["exam", "student"]

    def __str__(self):
        return f"{self.student.email} - {self.exam.title}"

    @classmethod
    def create_attempt(cls, exam, student):
        """Create a new attempt with randomized questions and options."""
        questions = exam.get_questions()

        question_ids = [q.id for q in questions]
        shuffled_ids = secure_shuffle(question_ids)

        # Store shuffled option IDs for each question
        option_orders = {}
        for q in questions:
            option_ids = list(q.options.values_list("id", flat=True))
            option_orders[str(q.id)] = secure_shuffle(option_ids)

        return cls.objects.create(
            exam=exam,
            student=student,
            question_order=shuffled_ids,
            option_orders=option_orders,
            total_questions=len(questions),
        )

    def get_question_at_index(self, index):
        """Get question at specific index in student's order."""
        from apps.questions.models import Question

        if 0 <= index < len(self.question_order):
            question_id = self.question_order[index]
            return Question.objects.get(id=question_id)
        return None

    def get_shuffled_options_for_question(self, question):
        """Get options in student's shuffled order for a question."""
        # Build option map from database
        option_map = {opt.id: opt.text for opt in question.options.all()}

        # Get the shuffled order for this question (list of option IDs)
        order = self.option_orders.get(str(question.id), list(option_map.keys()))

        options = []
        for idx, opt_id in enumerate(order):
            if opt_id in option_map:
                options.append(
                    {
                        "display_number": idx + 1,
                        "option_id": opt_id,
                        "text": option_map[opt_id],
                    }
                )
        return options

    def get_all_questions_with_options(self):
        """Get all questions with shuffled options and existing answers."""
        from apps.questions.models import Question

        questions = Question.objects.filter(
            id__in=self.question_order
        ).prefetch_related("options")
        questions_dict = {q.id: q for q in questions}

        # Get selected option IDs from answers
        answers = {a.question_id: a.selected_option_id for a in self.answers.all()}

        result = []
        for idx, q_id in enumerate(self.question_order):
            question = questions_dict.get(q_id)
            if question:
                result.append(
                    {
                        "index": idx,
                        "question": question,
                        "options": self.get_shuffled_options_for_question(question),
                        "selected_answer": answers.get(q_id),
                    }
                )
        return result

    def calculate_score(self):
        """Calculate and save the score."""
        correct_count = self.answers.filter(is_correct=True).count()
        self.score = correct_count
        self.save()
        return correct_count

    @property
    def is_time_expired(self):
        """Check if exam time has passed."""
        return timezone.now() > self.exam.end_time

    @property
    def percentage_score(self):
        """Return score as percentage."""
        if self.score is not None and self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 1)
        return 0


class ExamAnswer(models.Model):
    """Individual answer to a question within an attempt."""

    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
    )
    selected_option = models.ForeignKey(
        "questions.QuestionOption",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "exam_answers"
        verbose_name = "Exam Answer"
        verbose_name_plural = "Exam Answers"
        unique_together = ["attempt", "question"]

    def save(self, *args, **kwargs):
        """Auto-check if answer is correct."""
        if self.selected_option and self.question.correct_option:
            self.is_correct = self.selected_option_id == self.question.correct_option_id
        else:
            self.is_correct = False
        super().save(*args, **kwargs)
