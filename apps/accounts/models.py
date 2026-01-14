import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class School(models.Model):
    """
    Single school/college for this installation.
    Only ONE record should exist in this table.
    """

    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="school/", blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "school"
        verbose_name = "School"
        verbose_name_plural = "School"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one school exists
        if not self.pk and School.objects.exists():
            raise ValueError("Only one School can be created.")
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get the single school instance or None."""
        return cls.objects.first()

    @classmethod
    def exists(cls):
        """Check if school is registered."""
        return cls.objects.exists()


class OTPVerification(models.Model):
    """OTP verification for email."""

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "otp_verification"
        verbose_name = "OTP Verification"
        verbose_name_plural = "OTP Verifications"

    def __str__(self):
        return f"{self.email} - {self.otp}"

    @classmethod
    def generate_otp(cls, email):
        """Generate a 6-digit OTP for email."""
        # Delete old OTPs for this email
        cls.objects.filter(email=email).delete()

        otp = "".join(secrets.choice(string.digits) for _ in range(6))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)

        return cls.objects.create(email=email, otp=otp, expires_at=expires_at)

    def is_valid(self):
        """Check if OTP is still valid."""
        return not self.is_verified and timezone.now() < self.expires_at

    @classmethod
    def verify(cls, email, otp):
        """Verify OTP for email."""
        try:
            record = cls.objects.get(email=email, otp=otp, is_verified=False)
            if record.is_valid():
                record.is_verified = True
                record.save()
                return True
        except cls.DoesNotExist:
            pass
        return False


class Class(models.Model):
    """
    Class/Standard model for organizing students.
    Flexible naming: "Class 10", "X", "दहावी", "10th Standard", etc.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="For sorting classes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class Subject(models.Model):
    """Subject within a class (e.g., Mathematics for Class 10A)."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subjects"
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["name"]
        unique_together = ["assigned_class", "name"]

    def __str__(self):
        return f"{self.name} ({self.assigned_class.name})"


class User(AbstractUser):
    """Custom User model with role-based access."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        EXAMINER = "examiner", "Examiner"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        help_text="Only applicable for students",
    )

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

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


class Invitation(models.Model):
    """Invitation for new users to join the system."""

    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=User.Role.choices)
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
    )
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invitations_sent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitations"
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"

    def __str__(self):
        return f"Invite: {self.email} ({self.role})"

    @classmethod
    def create_invitation(
        cls, email, first_name, last_name, phone, role, invited_by, assigned_class=None
    ):
        """Create invitation with secure token."""
        # Delete any existing pending invitations for this email
        cls.objects.filter(email=email.lower(), accepted_at__isnull=True).delete()

        token = secrets.token_urlsafe(48)
        expires_at = timezone.now() + timezone.timedelta(days=7)

        return cls.objects.create(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            assigned_class=assigned_class,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at,
        )

    def is_valid(self):
        """Check if invitation is still valid."""
        return self.accepted_at is None and timezone.now() < self.expires_at

    def get_invite_url(self):
        """Get the invitation acceptance URL."""
        from django.urls import reverse

        return reverse("accounts:accept_invite", kwargs={"token": self.token})
