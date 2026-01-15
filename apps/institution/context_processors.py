from .models import Institution


def institution_context(request):
    """Add institution instance to template context."""
    return {"institution": Institution.get_instance()}
