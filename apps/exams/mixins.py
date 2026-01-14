from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class StudentRequiredMixin(LoginRequiredMixin):
    """Mixin that requires student role to access exam-taking views."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_student:
            messages.error(request, "Only students can access exams.")
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)
