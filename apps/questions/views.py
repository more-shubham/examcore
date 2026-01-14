from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.accounts.models import Subject

from .forms import QuestionForm
from .mixins import QuestionManagerRequiredMixin
from .models import Question


class QuestionBankView(QuestionManagerRequiredMixin, View):
    """View to list all questions with filtering by subject."""

    template_name = "questions/question_list.html"
    paginate_by = 20

    def get(self, request):
        questions = Question.objects.filter(is_active=True).select_related(
            "subject", "subject__assigned_class", "created_by"
        )

        # Filter by subject if provided
        subject_id = request.GET.get("subject")
        if subject_id:
            questions = questions.filter(subject_id=subject_id)

        # Search by question text
        search = request.GET.get("search")
        if search:
            questions = questions.filter(question_text__icontains=search)

        # Pagination
        paginator = Paginator(questions, self.paginate_by)
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
            "search": search or "",
            "total_questions": questions.count(),
        }
        return render(request, self.template_name, context)


class QuestionCreateView(QuestionManagerRequiredMixin, View):
    """View to create a new question."""

    template_name = "questions/question_form.html"

    def get(self, request):
        form = QuestionForm()
        # Pre-select subject if provided in URL
        subject_id = request.GET.get("subject")
        if subject_id:
            form.fields["subject"].initial = subject_id
        return render(request, self.template_name, {"form": form, "is_edit": False})

    def post(self, request):
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()
            messages.success(request, "Question added successfully.")
            return redirect("questions:list")
        return render(request, self.template_name, {"form": form, "is_edit": False})


class QuestionUpdateView(QuestionManagerRequiredMixin, View):
    """View to edit an existing question."""

    template_name = "questions/question_form.html"

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk, is_active=True)
        # Only creator or admin can edit
        if not (request.user.is_admin or question.created_by == request.user):
            messages.error(request, "You can only edit your own questions.")
            return redirect("questions:list")
        form = QuestionForm(instance=question)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "question": question},
        )

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk, is_active=True)
        # Only creator or admin can edit
        if not (request.user.is_admin or question.created_by == request.user):
            messages.error(request, "You can only edit your own questions.")
            return redirect("questions:list")
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            return redirect("questions:list")
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "question": question},
        )


class QuestionDeleteView(QuestionManagerRequiredMixin, View):
    """View to delete a question (soft delete)."""

    template_name = "questions/question_confirm_delete.html"

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk, is_active=True)
        # Only creator or admin can delete
        if not (request.user.is_admin or question.created_by == request.user):
            messages.error(request, "You can only delete your own questions.")
            return redirect("questions:list")
        return render(request, self.template_name, {"question": question})

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk, is_active=True)
        # Only creator or admin can delete
        if not (request.user.is_admin or question.created_by == request.user):
            messages.error(request, "You can only delete your own questions.")
            return redirect("questions:list")
        # Soft delete
        question.is_active = False
        question.save()
        messages.success(request, "Question deleted successfully.")
        return redirect("questions:list")
