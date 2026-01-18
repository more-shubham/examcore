import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.attempts.models import ExamAttempt

logger = logging.getLogger(__name__)


# Store old status before save to detect status change
@receiver(pre_save, sender=ExamAttempt)
def store_old_attempt_status(sender, instance, **kwargs):
    """Store the old status before saving to detect status changes."""
    if instance.pk:
        try:
            old_instance = ExamAttempt.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except ExamAttempt.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=ExamAttempt)
def notify_result_available(sender, instance, created, **kwargs):
    """Send notification when exam is submitted and result is available."""
    from apps.core.services.notification import NotificationService

    old_status = getattr(instance, "_old_status", None)

    # Only notify if status changed to submitted or timed_out
    # (meaning the result is now available)
    completed_statuses = [ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT]

    # Only notify if status just changed to completed (not on every save)
    if (
        instance.status in completed_statuses
        and old_status
        and old_status not in completed_statuses
    ):
        try:
            NotificationService.notify_result_available(instance)
        except Exception as e:
            logger.error(f"Failed to send result notification: {e}")
