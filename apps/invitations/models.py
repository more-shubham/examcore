import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.core.models import TimestampedModel


class Invitation(TimestampedModel):
    """Invitation for new user registration."""

    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20)
    assigned_class = models.ForeignKey(
        "academic.Class",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
    )
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invitations_sent",
    )
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitations"
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"
        indexes = [
            models.Index(
                fields=["email", "accepted_at"], name="invitations_email_accepted_idx"
            ),
            models.Index(
                fields=["expires_at", "accepted_at"], name="invitations_expiry_idx"
            ),
        ]

    def __str__(self):
        return f"Invitation for {self.email}"

    @classmethod
    def create_invitation(
        cls, email, first_name, last_name, phone, role, invited_by, assigned_class=None
    ):
        """Create a new invitation with secure token."""
        # Delete any existing pending invitations for this email
        cls.objects.filter(email=email.lower(), accepted_at__isnull=True).delete()

        return cls.objects.create(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            assigned_class=assigned_class,
            token=secrets.token_urlsafe(48),
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=7),
        )

    def is_valid(self):
        """Check if invitation is still valid."""
        return self.accepted_at is None and timezone.now() < self.expires_at

    def get_invite_url(self):
        """Get the full invitation URL."""
        return reverse("invitations:accept", kwargs={"token": self.token})
