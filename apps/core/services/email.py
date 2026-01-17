import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""

    @staticmethod
    def send_otp_email(email: str, otp: str) -> bool:
        """Send OTP verification email."""
        subject = "Your Verification Code"
        message = (
            f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."
        )
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")
            return False

    @staticmethod
    def send_invitation_email(email: str, invite_url: str, inviter_name: str) -> bool:
        """Send invitation email to new user."""
        subject = "You've Been Invited to ExamCore"
        message = f"""Hello,

You have been invited by {inviter_name} to join ExamCore.

Click the link below to set up your account:
{invite_url}

This link will expire in 7 days.

Best regards,
ExamCore Team
"""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send invitation email to {email}: {e}")
            return False

    @staticmethod
    def send_password_reset_email(email: str, otp: str) -> bool:
        """Send password reset OTP email."""
        subject = "Password Reset Code"
        message = f"Your password reset code is: {otp}\n\nThis code will expire in 10 minutes."
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
