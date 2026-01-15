import json

from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.core.mixins import AdminRequiredMixin

from .forms import ClassForm, SubjectForm
from .models import Class, Subject


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
