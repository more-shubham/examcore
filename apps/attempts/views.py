from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.core.mixins import StudentRequiredMixin
from apps.exams.models import Exam

from .models import ExamAnswer, ExamAttempt


class StudentExamListView(StudentRequiredMixin, View):
    """List available exams for student."""

    template_name = "attempts/exam_list.html"

    def get(self, request):
        user = request.user

        exams = Exam.objects.filter(
            subject__assigned_class=user.assigned_class,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        ).select_related("subject", "subject__assigned_class")

        attempts = {
            a.exam_id: a
            for a in ExamAttempt.objects.filter(student=user, exam__in=exams)
        }

        upcoming_exams = []
        active_exams = []
        past_exams = []

        for exam in exams:
            exam_data = {
                "exam": exam,
                "attempt": attempts.get(exam.id),
            }
            if exam.is_upcoming:
                upcoming_exams.append(exam_data)
            elif exam.is_running:
                active_exams.append(exam_data)
            else:
                past_exams.append(exam_data)

        return render(
            request,
            self.template_name,
            {
                "upcoming_exams": upcoming_exams,
                "active_exams": active_exams,
                "past_exams": past_exams,
            },
        )


class StudentStartExamView(StudentRequiredMixin, View):
    """Start exam confirmation page."""

    template_name = "attempts/exam_start.html"

    def get_exam(self, pk):
        return get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        )

    def get(self, request, pk):
        exam = self.get_exam(pk)

        if exam.subject.assigned_class != request.user.assigned_class:
            messages.error(request, "You are not enrolled in this class.")
            return redirect("attempts:list")

        if not exam.is_running:
            if exam.is_upcoming:
                messages.info(request, "This exam has not started yet.")
            else:
                messages.warning(request, "This exam has ended.")
            return redirect("attempts:list")

        try:
            attempt = ExamAttempt.objects.get(exam=exam, student=request.user)
            if attempt.status == ExamAttempt.Status.SUBMITTED:
                return redirect("attempts:result", pk=exam.pk)
            return redirect("attempts:take", pk=exam.pk)
        except ExamAttempt.DoesNotExist:
            pass

        return render(request, self.template_name, {"exam": exam})

    def post(self, request, pk):
        exam = self.get_exam(pk)

        if exam.subject.assigned_class != request.user.assigned_class:
            messages.error(request, "You are not enrolled in this class.")
            return redirect("attempts:list")

        if not exam.is_running:
            messages.error(request, "This exam is not available.")
            return redirect("attempts:list")

        try:
            ExamAttempt.objects.get(exam=exam, student=request.user)
        except ExamAttempt.DoesNotExist:
            ExamAttempt.create_attempt(exam, request.user)

        return redirect("attempts:take", pk=exam.pk)


class StudentExamView(StudentRequiredMixin, View):
    """Main exam-taking interface."""

    template_name = "attempts/exam_take.html"

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
            status=Exam.Status.PUBLISHED,
        )

        try:
            attempt = ExamAttempt.objects.select_related("exam").get(
                exam=exam, student=request.user
            )
        except ExamAttempt.DoesNotExist:
            return redirect("attempts:start", pk=pk)

        if attempt.status == ExamAttempt.Status.SUBMITTED:
            return redirect("attempts:result", pk=pk)

        if attempt.is_time_expired:
            attempt.status = ExamAttempt.Status.TIMED_OUT
            attempt.submitted_at = exam.end_time
            attempt.save()
            attempt.calculate_score()
            messages.warning(
                request, "Time expired. Your exam has been auto-submitted."
            )
            return redirect("attempts:result", pk=pk)

        questions_data = attempt.get_all_questions_with_options()
        time_remaining = (exam.end_time - timezone.now()).total_seconds()

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "attempt": attempt,
                "questions_data": questions_data,
                "time_remaining": max(0, int(time_remaining)),
            },
        )

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        attempt = get_object_or_404(ExamAttempt, exam=exam, student=request.user)

        if attempt.status != ExamAttempt.Status.IN_PROGRESS:
            return redirect("attempts:result", pk=pk)

        # Save answers - value is now the option ID (integer)
        for key, value in request.POST.items():
            if key.startswith("question_") and value:
                question_id = key.replace("question_", "")
                try:
                    option_id = int(value)
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option_id": option_id},
                    )
                except (ValueError, TypeError):
                    continue

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name, {"saved": True})

        return redirect("attempts:take", pk=pk)


class StudentSubmitExamView(StudentRequiredMixin, View):
    """Submit exam and finalize score."""

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        attempt = get_object_or_404(ExamAttempt, exam=exam, student=request.user)

        if attempt.status == ExamAttempt.Status.SUBMITTED:
            return redirect("attempts:result", pk=pk)

        # Save answers - value is now the option ID (integer)
        for key, value in request.POST.items():
            if key.startswith("question_") and value:
                question_id = key.replace("question_", "")
                try:
                    option_id = int(value)
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option_id": option_id},
                    )
                except (ValueError, TypeError):
                    continue

        attempt.status = ExamAttempt.Status.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.save()
        attempt.calculate_score()

        messages.success(request, "Exam submitted successfully!")
        return redirect("attempts:result", pk=pk)


class StudentResultView(StudentRequiredMixin, View):
    """Display exam results."""

    template_name = "attempts/exam_result.html"

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
        )
        attempt = get_object_or_404(
            ExamAttempt.objects.prefetch_related(
                "answers", "answers__question", "answers__selected_option"
            ),
            exam=exam,
            student=request.user,
        )

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "attempt": attempt,
            },
        )
