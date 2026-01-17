from django.db import models

from apps.core.models import TimestampedModel


class Class(TimestampedModel):
    """Class/Standard/Grade for grouping students."""

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    cached_student_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "classes"
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["is_active"], name="classes_active_idx"),
        ]

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        """Return cached count of active students in this class."""
        return self.cached_student_count

    def update_student_count(self):
        """Update the cached student count from the database."""
        count = self.students.filter(is_active=True).count()
        if self.cached_student_count != count:
            self.cached_student_count = count
            self.save(update_fields=["cached_student_count"])


class Subject(TimestampedModel):
    """Subject within a class."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["assigned_class", "name"], name="unique_subject_per_class"
            ),
        ]
        indexes = [
            models.Index(fields=["is_active"], name="subjects_active_idx"),
            models.Index(
                fields=["assigned_class", "is_active"], name="subjects_class_active_idx"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.assigned_class.name})"
