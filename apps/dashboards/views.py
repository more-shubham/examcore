from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from apps.institution.models import Institution


class DashboardView(LoginRequiredMixin, View):
    """Role-specific dashboard."""

    def get_template(self, user):
        if user.is_student:
            return "dashboards/student.html"
        elif user.is_teacher:
            return "dashboards/teacher.html"
        elif user.is_examiner:
            return "dashboards/examiner.html"
        return "dashboards/admin.html"

    def get(self, request):
        user = request.user
        institution = Institution.get_instance()
        context = {"institution": institution}

        if user.is_student:
            context.update(self.get_student_context(user))
        elif user.is_examiner:
            context.update(self.get_examiner_context(user))
        elif user.is_admin:
            context.update(self.get_admin_context())

        return render(request, self.get_template(user), context)

    def get_student_context(self, user):
        from apps.attempts.models import ExamAttempt
        from apps.exams.models import Exam

        if not user.assigned_class:
            return {
                "active_exam_count": 0,
                "total_exam_count": 0,
                "completed_exam_count": 0,
            }

        exams = Exam.objects.filter(
            subject__assigned_class=user.assigned_class,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        )

        attempts = ExamAttempt.objects.filter(
            student=user,
            status=ExamAttempt.Status.SUBMITTED,
        )

        active_count = sum(1 for e in exams if e.is_running)

        return {
            "active_exam_count": active_count,
            "total_exam_count": exams.count(),
            "completed_exam_count": attempts.count(),
        }

    def get_examiner_context(self, user):
        from apps.exams.models import Exam
        from apps.questions.models import Question

        return {
            "question_count": Question.objects.filter(created_by=user).count(),
            "exam_count": Exam.objects.filter(created_by=user).count(),
        }

    def get_admin_context(self):
        from django.contrib.auth import get_user_model

        from apps.academic.models import Class
        from apps.exams.models import Exam
        from apps.questions.models import Question

        User = get_user_model()

        return {
            "question_count": Question.objects.filter(is_active=True).count(),
            "exam_count": Exam.objects.filter(is_active=True).count(),
            "examiner_count": User.objects.filter(
                role=User.Role.EXAMINER, is_active=True
            ).count(),
            "teacher_count": User.objects.filter(
                role=User.Role.TEACHER, is_active=True
            ).count(),
            "class_count": Class.objects.filter(is_active=True).count(),
            "student_count": User.objects.filter(
                role=User.Role.STUDENT, is_active=True
            ).count(),
        }
