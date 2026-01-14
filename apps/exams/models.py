import secrets

from django.db import models
from django.utils import timezone


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
        "accounts.Subject",
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
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="exams_created",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exams"
        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        ordering = ["-start_time"]

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
        unique_together = ["exam", "question"]
        ordering = ["order"]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order + 1}"


def secure_shuffle(items):
    """Cryptographically secure shuffle using secrets module."""
    items = list(items)
    shuffled = []
    while items:
        index = secrets.randbelow(len(items))
        shuffled.append(items.pop(index))
    return shuffled


class ExamAttempt(models.Model):
    """Tracks a student's attempt at an exam with their unique randomization."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        TIMED_OUT = "timed_out", "Timed Out"

    # Core relations
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    student = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="exam_attempts",
    )

    # Randomization data (stored as JSON)
    question_order = models.JSONField()  # List of question IDs in randomized order
    option_orders = models.JSONField()  # Dict: {question_id: ["B", "D", "A", "C"]}

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Status & Score
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    score = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField()

    class Meta:
        db_table = "exam_attempts"
        verbose_name = "Exam Attempt"
        verbose_name_plural = "Exam Attempts"
        unique_together = ["exam", "student"]  # One attempt per student per exam
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.email} - {self.exam.title}"

    @classmethod
    def create_attempt(cls, exam, student):
        """
        Create a new exam attempt with randomized question and option orders.

        This generates unique randomization for this student that stays
        consistent throughout their exam attempt.
        """
        # Get questions for this exam
        questions = exam.get_questions()
        question_ids = [q.id for q in questions]

        # Shuffle question order (unique per student)
        shuffled_questions = secure_shuffle(question_ids)

        # Shuffle option order for EACH question
        option_orders = {}
        for q_id in question_ids:
            option_orders[str(q_id)] = secure_shuffle(["A", "B", "C", "D"])

        # Create the attempt
        return cls.objects.create(
            exam=exam,
            student=student,
            question_order=shuffled_questions,
            option_orders=option_orders,
            total_questions=len(questions),
        )

    def get_question_at_index(self, index):
        """Get question at specific index in this student's order."""
        if index < 0 or index >= len(self.question_order):
            return None
        from apps.questions.models import Question

        question_id = self.question_order[index]
        return Question.objects.get(id=question_id)

    def get_shuffled_options_for_question(self, question):
        """Get options in this student's random order for a question."""
        option_order = self.option_orders.get(str(question.id), ["A", "B", "C", "D"])
        options = []
        for i, original_key in enumerate(option_order, start=1):
            options.append(
                {
                    "display_number": i,
                    "text": getattr(question, f"option_{original_key.lower()}"),
                    "original_key": original_key,
                }
            )
        return options

    def get_all_questions_with_options(self):
        """Get all questions with their shuffled options for this attempt."""
        from apps.questions.models import Question

        questions_data = []
        question_ids = self.question_order
        questions = Question.objects.filter(id__in=question_ids)
        questions_dict = {q.id: q for q in questions}

        # Get existing answers
        answers = {a.question_id: a.selected_option for a in self.answers.all()}

        for idx, q_id in enumerate(question_ids):
            question = questions_dict.get(q_id)
            if question:
                options = self.get_shuffled_options_for_question(question)
                questions_data.append(
                    {
                        "index": idx,
                        "question": question,
                        "options": options,
                        "selected_answer": answers.get(q_id),
                    }
                )
        return questions_data

    def calculate_score(self):
        """Calculate and save the score based on answers."""
        correct_count = self.answers.filter(is_correct=True).count()
        self.score = correct_count
        self.save(update_fields=["score"])
        return correct_count

    @property
    def is_time_expired(self):
        """Check if exam time has expired."""
        return timezone.now() > self.exam.end_time

    @property
    def percentage_score(self):
        """Return score as percentage."""
        if self.score is None or self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 1)


class ExamAnswer(models.Model):
    """Stores a student's answer to a question."""

    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
        related_name="exam_answers",
    )
    selected_option = models.CharField(
        max_length=1,
        null=True,
        blank=True,
    )  # A, B, C, or D (original key)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "exam_answers"
        verbose_name = "Exam Answer"
        verbose_name_plural = "Exam Answers"
        unique_together = ["attempt", "question"]

    def __str__(self):
        return f"{self.attempt.student.email} - Q{self.question.id}: {self.selected_option}"

    def save(self, *args, **kwargs):
        """Automatically check if answer is correct when saving."""
        if self.selected_option:
            self.is_correct = self.selected_option == self.question.correct_option
        else:
            self.is_correct = False
        super().save(*args, **kwargs)
