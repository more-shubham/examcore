from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with roles."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EXAMINER = "examiner", "Examiner"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    assigned_class = models.ForeignKey(
        "academic.Class",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_examiner(self):
        return self.role == self.Role.EXAMINER

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
