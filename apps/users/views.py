from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.academic.models import Class
from apps.core.mixins import AdminRequiredMixin
from apps.core.services.email import EmailService
from apps.invitations.models import Invitation

from .forms import AddExaminerForm, AddStudentForm, AddTeacherForm
from .models import User


class ExaminerManagementView(AdminRequiredMixin, View):
    """Manage examiner accounts."""

    template_name = "users/examiners.html"

    def get(self, request):
        examiners = User.objects.filter(role=User.Role.EXAMINER)
        pending_invitations = Invitation.objects.filter(
            role=User.Role.EXAMINER,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        form = AddExaminerForm()
        return render(
            request,
            self.template_name,
            {
                "examiners": examiners,
                "pending_invitations": pending_invitations,
                "form": form,
            },
        )

    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            form = AddExaminerForm(request.POST)
            if form.is_valid():
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.EXAMINER,
                    invited_by=request.user,
                )
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                email_sent = EmailService.send_invitation_email(
                    invitation.email,
                    invite_url,
                    request.user.get_full_name(),
                )
                if email_sent:
                    messages.success(request, f"Invitation sent to {invitation.email}")
                else:
                    messages.warning(
                        request,
                        f"Invitation created but email could not be sent to {invitation.email}",
                    )
                return redirect("users:examiners")
            return render(
                request,
                self.template_name,
                {
                    "examiners": User.objects.filter(role=User.Role.EXAMINER),
                    "pending_invitations": Invitation.objects.filter(
                        role=User.Role.EXAMINER,
                        accepted_at__isnull=True,
                        expires_at__gt=timezone.now(),
                    ),
                    "form": form,
                    "show_modal": True,
                },
            )

        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, id=user_id, role=User.Role.EXAMINER)
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"Examiner {user.get_full_name()} {status}.")

        return redirect("users:examiners")


class TeacherManagementView(AdminRequiredMixin, View):
    """Manage teacher accounts."""

    template_name = "users/teachers.html"

    def get(self, request):
        teachers = User.objects.filter(role=User.Role.TEACHER)
        pending_invitations = Invitation.objects.filter(
            role=User.Role.TEACHER,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        form = AddTeacherForm()
        return render(
            request,
            self.template_name,
            {
                "teachers": teachers,
                "pending_invitations": pending_invitations,
                "form": form,
            },
        )

    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            form = AddTeacherForm(request.POST)
            if form.is_valid():
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.TEACHER,
                    invited_by=request.user,
                )
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                email_sent = EmailService.send_invitation_email(
                    invitation.email,
                    invite_url,
                    request.user.get_full_name(),
                )
                if email_sent:
                    messages.success(request, f"Invitation sent to {invitation.email}")
                else:
                    messages.warning(
                        request,
                        f"Invitation created but email could not be sent to {invitation.email}",
                    )
                return redirect("users:teachers")
            return render(
                request,
                self.template_name,
                {
                    "teachers": User.objects.filter(role=User.Role.TEACHER),
                    "pending_invitations": Invitation.objects.filter(
                        role=User.Role.TEACHER,
                        accepted_at__isnull=True,
                        expires_at__gt=timezone.now(),
                    ),
                    "form": form,
                    "show_modal": True,
                },
            )

        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, id=user_id, role=User.Role.TEACHER)
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"Teacher {user.get_full_name()} {status}.")

        return redirect("users:teachers")


class StudentManagementView(AdminRequiredMixin, View):
    """Manage students within a class."""

    template_name = "users/students.html"

    def get_class(self, class_id):
        return get_object_or_404(Class, id=class_id)

    def get(self, request, class_id):
        selected_class = self.get_class(class_id)
        students = User.objects.filter(
            role=User.Role.STUDENT, assigned_class=selected_class
        )
        pending_invitations = Invitation.objects.filter(
            role=User.Role.STUDENT,
            assigned_class=selected_class,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        form = AddStudentForm(initial={"assigned_class": selected_class})
        return render(
            request,
            self.template_name,
            {
                "selected_class": selected_class,
                "students": students,
                "pending_invitations": pending_invitations,
                "form": form,
            },
        )

    def post(self, request, class_id):
        selected_class = self.get_class(class_id)
        action = request.POST.get("action")

        if action == "add":
            form = AddStudentForm(request.POST)
            if form.is_valid():
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.STUDENT,
                    invited_by=request.user,
                    assigned_class=selected_class,
                )
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                email_sent = EmailService.send_invitation_email(
                    invitation.email,
                    invite_url,
                    request.user.get_full_name(),
                )
                if email_sent:
                    messages.success(request, f"Invitation sent to {invitation.email}")
                else:
                    messages.warning(
                        request,
                        f"Invitation created but email could not be sent to {invitation.email}",
                    )
                return redirect("users:students", class_id=class_id)
            return render(
                request,
                self.template_name,
                {
                    "selected_class": selected_class,
                    "students": User.objects.filter(
                        role=User.Role.STUDENT, assigned_class=selected_class
                    ),
                    "pending_invitations": Invitation.objects.filter(
                        role=User.Role.STUDENT,
                        assigned_class=selected_class,
                        accepted_at__isnull=True,
                        expires_at__gt=timezone.now(),
                    ),
                    "form": form,
                    "show_modal": True,
                },
            )

        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            user = get_object_or_404(
                User, id=user_id, role=User.Role.STUDENT, assigned_class=selected_class
            )
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"Student {user.get_full_name()} {status}.")

        return redirect("users:students", class_id=class_id)
