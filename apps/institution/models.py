from django.core.cache import cache
from django.db import models

from apps.core.models import TimestampedModel


class Institution(TimestampedModel):
    """Institution configuration (School/College/University). Only one instance allowed."""

    CACHE_KEY = "institution_singleton"
    CACHE_TIMEOUT = 3600  # 1 hour

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
        self.clear_cache()

    def delete(self, *args, **kwargs):
        """Clear cache when institution is deleted."""
        super().delete(*args, **kwargs)
        Institution.clear_cache()

    @classmethod
    def get_instance(cls):
        """Get the single institution instance with caching."""
        instance = cache.get(cls.CACHE_KEY)
        if instance is None:
            instance = cls.objects.first()
            if instance:
                cache.set(cls.CACHE_KEY, instance, cls.CACHE_TIMEOUT)
        return instance

    @classmethod
    def clear_cache(cls):
        """Clear the institution cache."""
        cache.delete(cls.CACHE_KEY)

    @classmethod
    def exists(cls):
        """Check if institution has been registered."""
        return cls.get_instance() is not None
