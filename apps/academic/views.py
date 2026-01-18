import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.core.mixins import AdminRequiredMixin, StudentRequiredMixin
from apps.exams.models import Exam

from .forms import ClassForm, SubjectForm
from .models import Class, Subject

User = get_user_model()


class ClassManagementView(AdminRequiredMixin, View):
    """Manage classes."""

    template_name = "academic/classes/management.html"

    def get(self, request):
        classes = Class.objects.all()
        form = ClassForm()
        return render(
            request,
            self.template_name,
            {
                "classes": classes,
                "form": form,
            },
        )

    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            form = ClassForm(request.POST)
            if form.is_valid():
                cls = form.save(commit=False)
                max_order = (
                    Class.objects.aggregate(models.Max("order"))["order__max"] or 0
                )
                cls.order = max_order + 1
                cls.save()
                messages.success(request, f"Class '{cls.name}' created successfully.")
                return redirect("academic:classes")
            return render(
                request,
                self.template_name,
                {
                    "classes": Class.objects.all(),
                    "form": form,
                    "show_modal": True,
                },
            )

        elif action == "reorder":
            order_data = request.POST.get("order")
            if order_data:
                order_list = json.loads(order_data)
                for index, class_id in enumerate(order_list):
                    Class.objects.filter(id=class_id).update(order=index)
            return redirect("academic:classes")

        return redirect("academic:classes")


class SubjectManagementView(AdminRequiredMixin, View):
    """Manage subjects within a class."""

    template_name = "academic/subjects/management.html"

    def get_class(self, class_id):
        return get_object_or_404(Class, id=class_id)

    def get(self, request, class_id):
        selected_class = self.get_class(class_id)
        subjects = Subject.objects.filter(assigned_class=selected_class)
        form = SubjectForm()
        return render(
            request,
            self.template_name,
            {
                "selected_class": selected_class,
                "subjects": subjects,
                "form": form,
            },
        )

    def post(self, request, class_id):
        selected_class = self.get_class(class_id)
        action = request.POST.get("action")

        if action == "add":
            form = SubjectForm(request.POST)
            if form.is_valid():
                subject = form.save(commit=False)
                subject.assigned_class = selected_class
                subject.save()
                messages.success(
                    request, f"Subject '{subject.name}' added successfully."
                )
                return redirect("academic:subjects", class_id=class_id)
            return render(
                request,
                self.template_name,
                {
                    "selected_class": selected_class,
                    "subjects": Subject.objects.filter(assigned_class=selected_class),
                    "form": form,
                    "show_modal": True,
                },
            )

        elif action == "toggle_active":
            subject_id = request.POST.get("subject_id")
            subject = get_object_or_404(
                Subject, id=subject_id, assigned_class=selected_class
            )
            subject.is_active = not subject.is_active
            subject.save()
            status = "activated" if subject.is_active else "deactivated"
            messages.success(request, f"Subject '{subject.name}' {status}.")

        return redirect("academic:subjects", class_id=class_id)


class StudentClassView(StudentRequiredMixin, View):
    """View class information for students."""

    template_name = "academic/student_class.html"

    def get(self, request):
        student = request.user
        assigned_class = student.assigned_class

        if not assigned_class:
            messages.warning(request, "You are not assigned to any class yet.")
            return redirect("dashboards:home")

        # Get subjects for this class with exam counts
        now = timezone.now()
        subjects = Subject.objects.filter(
            assigned_class=assigned_class, is_active=True
        ).annotate(
            total_exams=Count(
                "exams",
                filter=Q(exams__is_active=True, exams__status=Exam.Status.PUBLISHED),
            ),
            upcoming_exams=Count(
                "exams",
                filter=Q(
                    exams__is_active=True,
                    exams__status=Exam.Status.PUBLISHED,
                    exams__start_time__gt=now,
                ),
            ),
        )

        # Get teachers for each subject
        subject_teachers = {}
        for subject in subjects:
            teachers = User.objects.filter(
                role=User.Role.TEACHER,
                is_active=True,
                assigned_subjects=subject,
            )
            subject_teachers[subject.id] = list(teachers)

        # Get student's completed exams per subject
        from apps.attempts.models import ExamAttempt

        completed_attempts = ExamAttempt.objects.filter(
            student=student,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        ).values_list("exam_id", flat=True)

        completed_exams_per_subject = {}
        for subject in subjects:
            completed_count = Exam.objects.filter(
                subject=subject,
                is_active=True,
                status=Exam.Status.PUBLISHED,
                id__in=completed_attempts,
            ).count()
            completed_exams_per_subject[subject.id] = completed_count

        # Get upcoming exams grouped by subject
        upcoming_exams = (
            Exam.objects.filter(
                subject__assigned_class=assigned_class,
                is_active=True,
                status=Exam.Status.PUBLISHED,
                start_time__gt=now,
            )
            .select_related("subject")
            .order_by("start_time")[:10]
        )

        return render(
            request,
            self.template_name,
            {
                "assigned_class": assigned_class,
                "subjects": subjects,
                "subject_teachers": subject_teachers,
                "completed_exams_per_subject": completed_exams_per_subject,
                "upcoming_exams": upcoming_exams,
            },
        )
