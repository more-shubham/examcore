from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.academic.models import Subject
from apps.core.mixins import QuestionManagerRequiredMixin
from apps.questions.models import Question

from .forms import ExamForm
from .models import Exam, ExamQuestion


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
        exam = get_object_or_404(
            Exam.objects.select_related(
                "subject", "subject__assigned_class", "created_by"
            ),
            pk=pk,
            is_active=True,
        )

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
        exam = get_object_or_404(
            Exam.objects.select_related(
                "subject", "subject__assigned_class", "created_by"
            ),
            pk=pk,
            is_active=True,
        )
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
        exam = get_object_or_404(
            Exam.objects.select_related("created_by"),
            pk=pk,
            is_active=True,
        )
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
        exam = get_object_or_404(
            Exam.objects.select_related(
                "subject", "subject__assigned_class", "created_by"
            ),
            pk=pk,
            is_active=True,
        )
        # Only creator or admin can delete
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only delete your own exams.")
            return redirect("exams:list")
        return render(request, self.template_name, {"exam": exam})

    def post(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("created_by"),
            pk=pk,
            is_active=True,
        )
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
        exam = get_object_or_404(
            Exam.objects.select_related(
                "subject", "subject__assigned_class", "created_by"
            ),
            pk=pk,
            is_active=True,
        )

        # Only creator or admin can manage questions
        if not (request.user.is_admin or exam.created_by == request.user):
            messages.error(request, "You can only manage questions for your own exams.")
            return redirect("exams:list")

        # Get all available questions for this subject
        available_questions = (
            Question.objects.filter(subject=exam.subject, is_active=True)
            .select_related("created_by")
            .prefetch_related("options")
        )

        # Get currently selected question IDs
        selected_ids = exam.exam_questions.values_list("question_id", flat=True)

        context = {
            "exam": exam,
            "available_questions": available_questions,
            "selected_ids": list(selected_ids),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("created_by"),
            pk=pk,
            is_active=True,
        )

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
