import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.exams.models import Exam

logger = logging.getLogger(__name__)


# Store old status before save to detect status change
@receiver(pre_save, sender=Exam)
def store_old_status(sender, instance, **kwargs):
    """Store the old status before saving to detect status changes."""
    if instance.pk:
        try:
            old_instance = Exam.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Exam.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Exam)
def notify_exam_published(sender, instance, created, **kwargs):
    """Send notification when an exam is published."""
    from apps.core.services.notification import NotificationService

    old_status = getattr(instance, "_old_status", None)

    # Only notify if:
    # 1. Exam was just created with published status, or
    # 2. Exam status changed from draft to published
    status_just_published = created or (
        old_status and old_status != Exam.Status.PUBLISHED
    )
    if instance.status == Exam.Status.PUBLISHED and status_just_published:
        try:
            NotificationService.notify_exam_published(instance)
        except Exception as e:
            logger.error(f"Failed to send exam published notifications: {e}")
