from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import UserManager


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
    assigned_subjects = models.ManyToManyField(
        "academic.Subject",
        blank=True,
        related_name="teachers",
        help_text="Subjects assigned to this teacher",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"], name="users_role_idx"),
            models.Index(fields=["role", "is_active"], name="users_role_active_idx"),
            models.Index(
                fields=["assigned_class", "is_active"], name="users_class_active_idx"
            ),
        ]

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


class NotificationPreference(models.Model):
    """User notification preferences."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    exam_published = models.BooleanField(
        default=True,
        help_text="Receive email when a new exam is published for your class",
    )
    exam_reminder = models.BooleanField(
        default=True,
        help_text="Receive reminder email 24 hours before exam starts",
    )
    result_available = models.BooleanField(
        default=True,
        help_text="Receive email when your exam result is available",
    )

    class Meta:
        db_table = "notification_preferences"
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"

    def __str__(self):
        return f"Notification Preferences for {self.user.email}"


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences when a new user is created."""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)
