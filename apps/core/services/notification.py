import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.services.email import EmailService

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Service for sending notifications to users based on their preferences."""

    @staticmethod
    def notify_exam_published(exam):
        """
        Send notification to all students in the exam's subject classes
        when an exam is published.
        """
        from apps.users.models import NotificationPreference

        # Get the subject and its assigned class
        subject = exam.subject
        assigned_class = subject.assigned_class

        # Get all active students in this class
        students = User.objects.filter(
            role=User.Role.STUDENT,
            is_active=True,
            assigned_class=assigned_class,
        ).select_related("notification_preferences")

        sent_count = 0
        for student in students:
            # Check notification preferences
            try:
                prefs = student.notification_preferences
                if not prefs.exam_published:
                    continue
            except NotificationPreference.DoesNotExist:
                # Create default preferences
                prefs = NotificationPreference.objects.create(user=student)
                if not prefs.exam_published:
                    continue

            # Send notification
            success = EmailService.send_exam_published_notification(
                email=student.email,
                student_name=student.get_full_name() or student.username,
                exam_title=exam.title,
                subject_name=subject.name,
                start_time=exam.start_time.strftime("%b %d, %Y %H:%M"),
                end_time=exam.end_time.strftime("%b %d, %Y %H:%M"),
            )
            if success:
                sent_count += 1

        logger.info(
            f"Sent exam published notification for '{exam.title}' to {sent_count} students"
        )
        return sent_count

    @staticmethod
    def notify_result_available(attempt):
        """Send notification when exam result is available."""
        from apps.users.models import NotificationPreference

        student = attempt.student
        exam = attempt.exam

        # Check notification preferences
        try:
            prefs = student.notification_preferences
            if not prefs.result_available:
                return False
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            NotificationPreference.objects.create(user=student)

        # Send notification
        success = EmailService.send_result_notification(
            email=student.email,
            student_name=student.get_full_name() or student.username,
            exam_title=exam.title,
            subject_name=exam.subject.name,
            score=attempt.score,
            total=attempt.total_questions,
            percentage=attempt.percentage_score,
        )

        if success:
            logger.info(
                f"Sent result notification to {student.email} for '{exam.title}'"
            )

        return success

    @staticmethod
    def send_exam_reminders():
        """
        Send reminder emails for exams starting within the next 24 hours.
        This should be run as a scheduled task (e.g., via cron or Celery).
        """
        from apps.exams.models import Exam
        from apps.users.models import NotificationPreference

        now = timezone.now()
        reminder_window_start = now
        reminder_window_end = now + timezone.timedelta(hours=24)

        # Find published exams starting within the next 24 hours
        upcoming_exams = Exam.objects.filter(
            status=Exam.Status.PUBLISHED,
            is_active=True,
            start_time__gte=reminder_window_start,
            start_time__lte=reminder_window_end,
        ).select_related("subject")

        total_sent = 0
        for exam in upcoming_exams:
            # Get the assigned class for this subject
            assigned_class = exam.subject.assigned_class

            # Get students in this class
            students = User.objects.filter(
                role=User.Role.STUDENT,
                is_active=True,
                assigned_class=assigned_class,
            ).select_related("notification_preferences")

            for student in students:
                # Check notification preferences
                try:
                    prefs = student.notification_preferences
                    if not prefs.exam_reminder:
                        continue
                except NotificationPreference.DoesNotExist:
                    prefs = NotificationPreference.objects.create(user=student)
                    if not prefs.exam_reminder:
                        continue

                # Send reminder
                success = EmailService.send_exam_reminder(
                    email=student.email,
                    student_name=student.get_full_name() or student.username,
                    exam_title=exam.title,
                    subject_name=exam.subject.name,
                    start_time=exam.start_time.strftime("%b %d, %Y %H:%M"),
                )
                if success:
                    total_sent += 1

        logger.info(f"Sent {total_sent} exam reminders")
        return total_sent
