from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be an admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)


class ExaminerRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be an examiner or admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_admin or request.user.is_examiner):
            messages.error(request, "Only examiners can access this page.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)


class TeacherRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be a teacher or admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_admin or request.user.is_teacher):
            messages.error(request, "Only teachers can access this page.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to be a student."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_student:
            messages.error(request, "Only students can access this page.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)


class QuestionManagerRequiredMixin(LoginRequiredMixin):
    """Mixin for views that require admin or examiner role (question management)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_admin or request.user.is_examiner):
            messages.error(request, "You don't have permission to manage questions.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)


class QuestionViewerRequiredMixin(LoginRequiredMixin):
    """Mixin for views that allow admin, examiner, or teacher to view questions."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (
            request.user.is_admin or request.user.is_examiner or request.user.is_teacher
        ):
            messages.error(request, "You don't have permission to view questions.")
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)
