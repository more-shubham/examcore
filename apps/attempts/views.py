from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.academic.models import Class
from apps.core.mixins import ResultsViewerRequiredMixin, StudentRequiredMixin
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


class TeacherResultsListView(ResultsViewerRequiredMixin, View):
    """List exam results for teacher's assigned subjects."""

    template_name = "attempts/teacher_results_list.html"
    paginate_by = 20

    def get(self, request):
        user = request.user

        # Get attempts based on user role
        attempts = ExamAttempt.objects.filter(
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT]
        ).select_related(
            "exam",
            "exam__subject",
            "exam__subject__assigned_class",
            "student",
        )

        # Teachers only see results from their assigned subjects
        if user.is_teacher and not user.is_admin and not user.is_examiner:
            assigned_subjects = user.assigned_subjects.filter(is_active=True)
            attempts = attempts.filter(exam__subject__in=assigned_subjects)
            exams = Exam.objects.filter(subject__in=assigned_subjects, is_active=True)
            classes = Class.objects.filter(
                id__in=assigned_subjects.values_list("assigned_class_id", flat=True)
            )
        else:
            exams = Exam.objects.filter(is_active=True)
            classes = Class.objects.filter(is_active=True)

        # Filter by exam if provided
        exam_id = request.GET.get("exam")
        if exam_id:
            attempts = attempts.filter(exam_id=exam_id)

        # Filter by class if provided
        class_id = request.GET.get("class")
        if class_id:
            attempts = attempts.filter(exam__subject__assigned_class_id=class_id)

        # Order by most recent first
        attempts = attempts.order_by("-submitted_at")

        # Pagination
        paginator = Paginator(attempts, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "exams": exams.select_related("subject"),
            "classes": classes,
            "selected_exam": exam_id,
            "selected_class": class_id,
            "total_results": attempts.count(),
        }
        return render(request, self.template_name, context)


class TeacherResultDetailView(ResultsViewerRequiredMixin, View):
    """View detailed result of a student's exam attempt."""

    template_name = "attempts/teacher_result_detail.html"

    def get(self, request, pk):
        user = request.user
        attempt = get_object_or_404(
            ExamAttempt.objects.select_related(
                "exam",
                "exam__subject",
                "exam__subject__assigned_class",
                "student",
            ).prefetch_related(
                "answers",
                "answers__question",
                "answers__question__options",
                "answers__selected_option",
            ),
            pk=pk,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        )

        # Teachers can only view results from their assigned subjects
        if user.is_teacher and not user.is_admin and not user.is_examiner:
            assigned_subject_ids = user.assigned_subjects.values_list("id", flat=True)
            if attempt.exam.subject_id not in assigned_subject_ids:
                messages.error(request, "You don't have access to this result.")
                return redirect("attempts:teacher_results")

        # Get answers with question details
        answers_data = []
        for answer in attempt.answers.all():
            question = answer.question
            answers_data.append(
                {
                    "question": question,
                    "selected_option": answer.selected_option,
                    "correct_option": question.correct_option,
                    "is_correct": answer.is_correct,
                    "options": list(question.options.all()),
                }
            )

        context = {
            "attempt": attempt,
            "exam": attempt.exam,
            "student": attempt.student,
            "answers_data": answers_data,
        }
        return render(request, self.template_name, context)
