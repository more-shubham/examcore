from django.db import models

from apps.core.models import TimestampedModel


class Class(TimestampedModel):
    """Class/Standard/Grade for grouping students."""

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "classes"
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        """Return count of active students in this class."""
        return self.students.filter(is_active=True).count()


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
        unique_together = ["assigned_class", "name"]

    def __str__(self):
        return f"{self.name} ({self.assigned_class.name})"
