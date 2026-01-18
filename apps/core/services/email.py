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

    @staticmethod
    def send_exam_published_notification(
        email: str,
        student_name: str,
        exam_title: str,
        subject_name: str,
        start_time: str,
        end_time: str,
    ) -> bool:
        """Send notification when a new exam is published."""
        subject = f"New Exam Available: {exam_title}"
        message = f"""Hello {student_name},

A new exam has been published for your class:

Exam: {exam_title}
Subject: {subject_name}
Start Time: {start_time}
End Time: {end_time}

Please log in to ExamCore to view more details.

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
            logger.error(f"Failed to send exam published notification to {email}: {e}")
            return False

    @staticmethod
    def send_exam_reminder(
        email: str,
        student_name: str,
        exam_title: str,
        subject_name: str,
        start_time: str,
    ) -> bool:
        """Send exam reminder 24 hours before start."""
        subject = f"Reminder: {exam_title} starts tomorrow"
        message = f"""Hello {student_name},

This is a reminder that your exam is starting soon:

Exam: {exam_title}
Subject: {subject_name}
Start Time: {start_time}

Please ensure you are prepared and log in on time.

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
            logger.error(f"Failed to send exam reminder to {email}: {e}")
            return False

    @staticmethod
    def send_result_notification(
        email: str,
        student_name: str,
        exam_title: str,
        subject_name: str,
        score: int,
        total: int,
        percentage: float,
    ) -> bool:
        """Send notification when exam result is available."""
        status = "passed" if percentage >= 50 else "did not pass"
        subject = f"Result Available: {exam_title}"
        message = f"""Hello {student_name},

Your exam result is now available:

Exam: {exam_title}
Subject: {subject_name}
Score: {score}/{total} ({percentage}%)
Status: You {status} this exam.

Log in to ExamCore to view your detailed result and review your answers.

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
            logger.error(f"Failed to send result notification to {email}: {e}")
            return False
