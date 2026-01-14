"""Context processors for accounts app."""

from .models import School


def school_context(request):
    """Add school to all templates."""
    return {
        'school': School.get_instance()
    }
