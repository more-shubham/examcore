from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.accounts.models import Subject
from apps.questions.mixins import QuestionManagerRequiredMixin
from apps.questions.models import Question

from .forms import ExamForm
from .mixins import StudentRequiredMixin
from .models import Exam, ExamAnswer, ExamAttempt, ExamQuestion


class ExamListView(QuestionManagerRequiredMixin, View):
    """View to list all exams with filtering by subject."""

    template_name = "exams/exam_list.html"
    paginate_by = 20

    def get(self, request):
        exams = Exam.objects.filter(is_active=True).select_related(
            "subject", "subject__assigned_class", "created_by"
        )

        # Filter by subject if provided
        subject_id = request.GET.get("subject")
        if subject_id:
            exams = exams.filter(subject_id=subject_id)

        # Filter by status
        status = request.GET.get("status")
        if status:
            exams = exams.filter(status=status)

        # Pagination
        paginator = Paginator(exams, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Get all subjects for filter dropdown
        subjects = Subject.objects.filter(is_active=True).select_related(
            "assigned_class"
        )

        context = {
            "page_obj": page_obj,
            "subjects": subjects,
            "selected_subject": subject_id,
            "selected_status": status,
            "total_exams": exams.count(),
        }
        return render(request, self.template_name, context)


class ExamCreateView(QuestionManagerRequiredMixin, View):
    """View to create a new exam."""

    template_name = "exams/exam_form.html"

    def get(self, request):
        form = ExamForm()
        # Pre-select subject if provided in URL
        subject_id = request.GET.get("subject")
        if subject_id:
            form.fields["subject"].initial = subject_id
        return render(request, self.template_name, {"form": form, "is_edit": False})

    def post(self, request):
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, "Exam created successfully.")

            # If using manual questions, redirect to question selection
            if not exam.use_random_questions:
                return redirect("exams:questions", pk=exam.pk)
            return redirect("exams:detail", pk=exam.pk)
        return render(request, self.template_name, {"form": form, "is_edit": False})


class ExamDetailView(QuestionManagerRequiredMixin, View):
    """View to see exam details and questions."""

    template_name = "exams/exam_detail.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        # Get questions count
        if exam.use_random_questions:
            available_questions = Question.objects.filter(
                subject=exam.subject, is_active=True
            ).count()
        else:
            available_questions = exam.exam_questions.count()

        context = {
            "exam": exam,
            "available_questions": available_questions,
        }
        return render(request, self.template_name, context)


class ExamUpdateView(QuestionManagerRequiredMixin, View):
    """View to edit an existing exam."""

    template_name = "exams/exam_form.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)
        # Only creator or admin can edit
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only edit your own exams.")
            return redirect("exams:list")
        form = ExamForm(instance=exam)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "exam": exam},
        )

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)
        # Only creator or admin can edit
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only edit your own exams.")
            return redirect("exams:list")
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect("exams:detail", pk=exam.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "exam": exam},
        )


class ExamDeleteView(QuestionManagerRequiredMixin, View):
    """View to delete an exam (soft delete)."""

    template_name = "exams/exam_confirm_delete.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)
        # Only creator or admin can delete
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only delete your own exams.")
            return redirect("exams:list")
        return render(request, self.template_name, {"exam": exam})

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)
        # Only creator or admin can delete
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only delete your own exams.")
            return redirect("exams:list")
        # Soft delete
        exam.is_active = False
        exam.save()
        messages.success(request, "Exam deleted successfully.")
        return redirect("exams:list")


class ExamQuestionsView(QuestionManagerRequiredMixin, View):
    """View to manage questions for an exam (manual selection mode)."""

    template_name = "exams/exam_questions.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        # Only creator or admin can manage questions
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only manage questions for your own exams.")
            return redirect("exams:list")

        # Get all available questions for this subject
        available_questions = Question.objects.filter(
            subject=exam.subject, is_active=True
        ).select_related("created_by")

        # Get currently selected question IDs
        selected_ids = exam.exam_questions.values_list("question_id", flat=True)

        context = {
            "exam": exam,
            "available_questions": available_questions,
            "selected_ids": list(selected_ids),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        # Only creator or admin can manage questions
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only manage questions for your own exams.")
            return redirect("exams:list")

        # Get selected question IDs from form
        selected_ids = request.POST.getlist("questions")

        # Clear existing and add new selections
        exam.exam_questions.all().delete()
        for order, question_id in enumerate(selected_ids):
            ExamQuestion.objects.create(
                exam=exam,
                question_id=question_id,
                order=order,
            )

        messages.success(request, f"Exam updated with {len(selected_ids)} questions.")
        return redirect("exams:detail", pk=exam.pk)


# =============================================================================
# STUDENT EXAM VIEWS
# =============================================================================


class StudentExamListView(StudentRequiredMixin, View):
    """View for students to see available exams for their class."""

    template_name = "exams/student_exam_list.html"

    def get(self, request):
        user = request.user

        # Get published exams for student's class (via subject)
        exams = (
            Exam.objects.filter(
                subject__assigned_class=user.assigned_class,
                status=Exam.Status.PUBLISHED,
                is_active=True,
            )
            .select_related("subject")
            .order_by("-start_time")
        )

        # Get student's attempts
        attempts = {
            a.exam_id: a
            for a in ExamAttempt.objects.filter(student=user, exam__in=exams)
        }

        # Categorize exams
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

        context = {
            "upcoming_exams": upcoming_exams,
            "active_exams": active_exams,
            "past_exams": past_exams,
        }
        return render(request, self.template_name, context)


class StudentStartExamView(StudentRequiredMixin, View):
    """View for students to start an exam (creates attempt with randomization)."""

    template_name = "exams/student_exam_start.html"

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam,
            pk=pk,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        )

        # Check if student is in the correct class (via subject)
        if request.user.assigned_class != exam.subject.assigned_class:
            messages.error(request, "This exam is not for your class.")
            return redirect("exams:student_list")

        # Check if exam is active
        if not exam.is_running:
            if exam.is_upcoming:
                messages.error(request, "This exam has not started yet.")
            else:
                messages.error(request, "This exam has ended.")
            return redirect("exams:student_list")

        # Check if already attempted
        existing_attempt = ExamAttempt.objects.filter(
            exam=exam, student=request.user
        ).first()

        if existing_attempt:
            if existing_attempt.status == ExamAttempt.Status.SUBMITTED:
                messages.info(request, "You have already completed this exam.")
                return redirect("exams:student_result", pk=pk)
            else:
                # Resume existing attempt
                return redirect("exams:student_take", pk=pk)

        context = {
            "exam": exam,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = get_object_or_404(
            Exam,
            pk=pk,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        )

        # Validate again (via subject)
        if request.user.assigned_class != exam.subject.assigned_class:
            messages.error(request, "This exam is not for your class.")
            return redirect("exams:student_list")

        if not exam.is_running:
            messages.error(request, "This exam is not currently active.")
            return redirect("exams:student_list")

        # Create attempt with randomization
        try:
            ExamAttempt.create_attempt(exam=exam, student=request.user)
            messages.success(request, "Exam started! Good luck!")
        except IntegrityError:
            # Already has an attempt
            pass

        return redirect("exams:student_take", pk=pk)


class StudentExamView(StudentRequiredMixin, View):
    """View for students to take the exam (answer questions)."""

    template_name = "exams/student_exam_take.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        # Get or check attempt
        attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()

        if not attempt:
            messages.error(request, "Please start the exam first.")
            return redirect("exams:student_start", pk=pk)

        if attempt.status == ExamAttempt.Status.SUBMITTED:
            messages.info(request, "You have already submitted this exam.")
            return redirect("exams:student_result", pk=pk)

        # Check if time expired
        if attempt.is_time_expired:
            attempt.status = ExamAttempt.Status.TIMED_OUT
            attempt.submitted_at = exam.end_time
            attempt.calculate_score()
            attempt.save()
            messages.warning(
                request, "Time expired. Your exam has been auto-submitted."
            )
            return redirect("exams:student_result", pk=pk)

        # Get all questions with shuffled options
        questions_data = attempt.get_all_questions_with_options()

        context = {
            "exam": exam,
            "attempt": attempt,
            "questions_data": questions_data,
            "time_remaining": (exam.end_time - timezone.now()).total_seconds(),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Save answers (AJAX or form submission)."""
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()

        if not attempt or attempt.status == ExamAttempt.Status.SUBMITTED:
            messages.error(request, "Cannot save answers.")
            return redirect("exams:student_list")

        # Save all answers from form
        for key, value in request.POST.items():
            if key.startswith("question_"):
                question_id = int(key.replace("question_", ""))
                if value:  # Only save if an answer was selected
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option": value},
                    )

        messages.success(request, "Answers saved.")
        return redirect("exams:student_take", pk=pk)


class StudentSubmitExamView(StudentRequiredMixin, View):
    """View to submit the exam and calculate score."""

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()

        if not attempt:
            messages.error(request, "No exam attempt found.")
            return redirect("exams:student_list")

        if attempt.status == ExamAttempt.Status.SUBMITTED:
            messages.info(request, "Exam already submitted.")
            return redirect("exams:student_result", pk=pk)

        # Save any remaining answers from form
        for key, value in request.POST.items():
            if key.startswith("question_"):
                question_id = int(key.replace("question_", ""))
                if value:
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option": value},
                    )

        # Mark as submitted
        attempt.status = ExamAttempt.Status.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.calculate_score()
        attempt.save()

        messages.success(request, "Exam submitted successfully!")
        return redirect("exams:student_result", pk=pk)


class StudentResultView(StudentRequiredMixin, View):
    """View to show exam result to student."""

    template_name = "exams/student_exam_result.html"

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, is_active=True)

        attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()

        if not attempt:
            messages.error(request, "No exam attempt found.")
            return redirect("exams:student_list")

        if attempt.status == ExamAttempt.Status.IN_PROGRESS:
            messages.info(request, "Please complete and submit the exam first.")
            return redirect("exams:student_take", pk=pk)

        context = {
            "exam": exam,
            "attempt": attempt,
        }
        return render(request, self.template_name, context)
