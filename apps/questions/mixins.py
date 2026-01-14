from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class QuestionManagerRequiredMixin(LoginRequiredMixin):
    """Mixin that requires admin or examiner role to manage questions."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_admin or request.user.is_examiner):
            messages.error(request, "Only Admins and Examiners can manage questions.")
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)
