"""Management command to refresh cached counts for all classes."""

from django.core.management.base import BaseCommand

from apps.academic.models import Class


class Command(BaseCommand):
    """Refresh cached student counts for all classes."""

    help = "Refresh cached student counts for all classes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--class-id",
            type=int,
            help="Refresh count for a specific class ID only",
        )

    def handle(self, *args, **options):
        class_id = options.get("class_id")

        if class_id:
            try:
                cls = Class.objects.get(pk=class_id)
                old_count = cls.cached_student_count
                cls.update_student_count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {cls.name}: {old_count} -> {cls.cached_student_count}"
                    )
                )
            except Class.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Class with ID {class_id} not found")
                )
                return
        else:
            classes = Class.objects.all()
            updated_count = 0

            for cls in classes:
                old_count = cls.cached_student_count
                cls.update_student_count()
                if old_count != cls.cached_student_count:
                    updated_count += 1
                    self.stdout.write(
                        f"Updated {cls.name}: {old_count} -> {cls.cached_student_count}"
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Refreshed counts for {classes.count()} classes. "
                    f"{updated_count} had changes."
                )
            )
