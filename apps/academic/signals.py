"""Signal handlers for academic app cache updates."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save


def setup_student_count_signals():
    """Set up signal handlers for student count updates."""
    User = get_user_model()

    post_save.connect(update_class_student_count_on_user_change, sender=User)
    post_delete.connect(update_class_student_count_on_user_delete, sender=User)


def update_class_student_count_on_user_change(sender, instance, **kwargs):
    """Update class student count when a user is created or updated."""
    # Update new class count if assigned
    if instance.assigned_class:
        instance.assigned_class.update_student_count()

    # If this is an update, we need to check if the class changed
    # We can detect this by checking if the instance has a pk
    if instance.pk:
        # Try to get the old instance to check if class changed
        try:
            User = sender
            old_instance = User.objects.get(pk=instance.pk)
            if (
                old_instance.assigned_class
                and old_instance.assigned_class != instance.assigned_class
            ):
                old_instance.assigned_class.update_student_count()
        except sender.DoesNotExist:
            pass


def update_class_student_count_on_user_delete(sender, instance, **kwargs):
    """Update class student count when a user is deleted."""
    if instance.assigned_class:
        instance.assigned_class.update_student_count()
