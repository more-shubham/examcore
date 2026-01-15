from django.db import models

from apps.core.models import TimestampedModel


class Institution(TimestampedModel):
    """Institution configuration (School/College/University). Only one instance allowed."""

    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="institution/", blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "institution"
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Ensure only one institution instance exists."""
        if not self.pk and Institution.objects.exists():
            raise ValueError("Only one Institution instance is allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get the single institution instance, or None if not set up."""
        return cls.objects.first()

    @classmethod
    def exists(cls):
        """Check if institution has been registered."""
        return cls.objects.exists()
