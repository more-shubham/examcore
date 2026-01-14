from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from apps.exams.models import Exam, ExamAttempt
from apps.questions.models import Question

from .forms import (
    AddExaminerForm,
    AddStudentForm,
    AddTeacherForm,
    ClassForm,
    ForgotPasswordForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
    SchoolSetupForm,
    SetPasswordForm,
    SubjectForm,
    VerifyOTPForm,
)
from .models import Class, Invitation, OTPVerification, School, Subject

User = get_user_model()


class AuthView(View):
    """
    True single-page authentication at /.
    Shows different forms based on state:
    - login: Admin exists
    - register: No admin, no session
    - verify: Session with email+password, OTP not verified
    - school: OTP verified, school not created
    """

    template_name = "accounts/auth.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_mode(self, request):
        """Determine which form to show based on state."""
        # If admin exists → login mode
        if User.objects.filter(role=User.Role.ADMIN).exists():
            return "login"

        # Check registration session
        registration = request.session.get("registration", {})

        # OTP verified but no school → school setup
        if registration.get("otp_verified") and not School.exists():
            return "school"

        # Has email+password but OTP not verified → verify
        if (
            registration.get("email")
            and registration.get("password")
            and not registration.get("otp_verified")
        ):
            return "verify"

        # Default: register
        return "register"

    def get_context(self, request, mode):
        """Return context with appropriate form."""
        context = {"mode": mode}

        if mode == "login":
            context["form"] = LoginForm()
            context["school"] = School.get_instance()
            context["step"] = None
        elif mode == "register":
            context["form"] = RegisterForm()
            context["step"] = 1
        elif mode == "verify":
            context["form"] = VerifyOTPForm()
            context["email"] = request.session.get("registration", {}).get("email", "")
            context["step"] = 2
        elif mode == "school":
            context["form"] = SchoolSetupForm()
            context["step"] = 3

        return context

    def get(self, request):
        mode = self.get_mode(request)
        context = self.get_context(request, mode)
        return render(request, self.template_name, context)

    def post(self, request):
        mode = self.get_mode(request)

        if mode == "login":
            return self.handle_login(request)
        elif mode == "register":
            return self.handle_register(request)
        elif mode == "verify":
            return self.handle_verify(request)
        elif mode == "school":
            return self.handle_school(request)

        return redirect("accounts:auth")

    def handle_login(self, request):
        """Handle login form submission."""
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next", "accounts:dashboard")
            return redirect(next_url)

        return render(
            request,
            self.template_name,
            {
                "mode": "login",
                "form": form,
                "school": School.get_instance(),
                "step": None,
            },
        )

    def handle_register(self, request):
        """Handle registration form submission."""
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Email is already normalized to lowercase by form.clean_email()
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Store in session
            request.session["registration"] = {
                "email": email,
                "password": password,
            }

            # Generate and send OTP
            otp_record = OTPVerification.generate_otp(email)

            # Send OTP email
            send_mail(
                subject="ExamCore - Verify Your Email",
                message=f"Your OTP is: {otp_record.otp}\n\nThis code expires in 10 minutes.",
                from_email="noreply@examcore.local",
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, f"OTP sent to {email}")
            return redirect("accounts:auth")

        return render(
            request,
            self.template_name,
            {
                "mode": "register",
                "form": form,
                "step": 1,
            },
        )

    def handle_verify(self, request):
        """Handle OTP verification form submission."""
        form = VerifyOTPForm(request.POST)
        email = request.session.get("registration", {}).get("email", "")

        if form.is_valid():
            otp = form.cleaned_data["otp"]

            if OTPVerification.verify(email, otp):
                request.session["registration"]["otp_verified"] = True
                request.session.modified = True

                messages.success(request, "Email verified successfully!")
                return redirect("accounts:auth")
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")

        return render(
            request,
            self.template_name,
            {
                "mode": "verify",
                "form": form,
                "email": email,
                "step": 2,
            },
        )

    def handle_school(self, request):
        """Handle school setup form submission."""
        form = SchoolSetupForm(request.POST, request.FILES)

        if form.is_valid():
            registration = request.session["registration"]

            # Create school
            school = form.save()

            # Create admin user (email is used as username, normalized to lowercase)
            email = registration["email"].lower()
            user = User.objects.create_user(
                username=email,
                email=email,
                password=registration["password"],
                role=User.Role.ADMIN,
                is_staff=True,
            )

            # Clear registration session
            del request.session["registration"]

            # Log in the user
            login(request, user)

            messages.success(
                request, f"Welcome to {school.name}! Your account is ready."
            )
            return redirect("accounts:dashboard")

        return render(
            request,
            self.template_name,
            {
                "mode": "school",
                "form": form,
                "step": 3,
            },
        )


class CustomLogoutView(BaseLogoutView):
    """Custom logout view."""

    def get_success_url(self):
        return "/"


class ResendOTPView(View):
    """Resend OTP."""

    def post(self, request):
        registration = request.session.get("registration", {})
        email = registration.get("email")

        if not email:
            messages.error(request, "Session expired. Please start again.")
            return redirect("accounts:auth")

        # Generate new OTP
        otp_record = OTPVerification.generate_otp(email)

        # Send OTP email
        send_mail(
            subject="ExamCore - Verify Your Email",
            message=f"Your new OTP is: {otp_record.otp}\n\nThis code expires in 10 minutes.",
            from_email="noreply@examcore.local",
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, f"New OTP sent to {email}")
        return redirect("accounts:auth")


class ForgotPasswordView(View):
    """View for requesting password reset."""

    template_name = "accounts/forgot_password.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        school = School.get_instance()
        return render(
            request,
            self.template_name,
            {
                "form": ForgotPasswordForm(),
                "school": school,
            },
        )

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        school = School.get_instance()

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Store email in session for reset step
            request.session["password_reset"] = {"email": email}

            # Generate and send OTP
            otp_record = OTPVerification.generate_otp(email)

            send_mail(
                subject="ExamCore - Password Reset OTP",
                message=f"Your password reset OTP is: {otp_record.otp}\n\nThis code expires in 10 minutes.",
                from_email="noreply@examcore.local",
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, f"OTP sent to {email}")
            return redirect("accounts:reset_password")

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "school": school,
            },
        )


class ResetPasswordView(View):
    """View for resetting password with OTP."""

    template_name = "accounts/reset_password.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        # Check if password reset session exists
        if not request.session.get("password_reset", {}).get("email"):
            messages.error(request, "Please start the password reset process.")
            return redirect("accounts:forgot_password")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        email = request.session.get("password_reset", {}).get("email", "")
        school = School.get_instance()
        return render(
            request,
            self.template_name,
            {
                "form": ResetPasswordForm(),
                "email": email,
                "school": school,
            },
        )

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        email = request.session.get("password_reset", {}).get("email", "")
        school = School.get_instance()

        if form.is_valid():
            otp = form.cleaned_data["otp"]

            if OTPVerification.verify(email, otp):
                # Update user password
                try:
                    user = User.objects.get(email=email, is_active=True)
                    user.set_password(form.cleaned_data["password"])
                    user.save()

                    # Clear session
                    del request.session["password_reset"]

                    messages.success(
                        request, "Password reset successful! Please sign in."
                    )
                    return redirect("accounts:auth")
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "email": email,
                "school": school,
            },
        )


class AcceptInviteView(View):
    """View for accepting invitation and setting password."""

    template_name = "accounts/accept_invite.html"

    def dispatch(self, request, *args, **kwargs):
        # If user is already logged in, redirect to dashboard
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_invitation(self, token):
        """Get and validate invitation."""
        try:
            return Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return None

    def get(self, request, token):
        invitation = self.get_invitation(token)

        if not invitation:
            messages.error(request, "Invalid invitation link.")
            return redirect("accounts:auth")

        if not invitation.is_valid():
            messages.error(
                request, "This invitation has expired or has already been used."
            )
            return redirect("accounts:auth")

        school = School.get_instance()
        return render(
            request,
            self.template_name,
            {
                "invitation": invitation,
                "form": SetPasswordForm(),
                "school": school,
            },
        )

    def post(self, request, token):
        invitation = self.get_invitation(token)

        if not invitation:
            messages.error(request, "Invalid invitation link.")
            return redirect("accounts:auth")

        if not invitation.is_valid():
            messages.error(
                request, "This invitation has expired or has already been used."
            )
            return redirect("accounts:auth")

        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Create user from invitation
            user = User.objects.create_user(
                username=invitation.email,
                email=invitation.email,
                password=form.cleaned_data["password"],
                first_name=invitation.first_name,
                last_name=invitation.last_name,
                phone=invitation.phone,
                role=invitation.role,
                assigned_class=invitation.assigned_class,
                is_active=True,
            )

            # Mark invitation as accepted
            invitation.accepted_at = timezone.now()
            invitation.save()

            # Log in user
            login(request, user)

            messages.success(request, f"Welcome to ExamCore, {user.get_full_name()}!")
            return redirect("accounts:dashboard")

        school = School.get_instance()
        return render(
            request,
            self.template_name,
            {
                "invitation": invitation,
                "form": form,
                "school": school,
            },
        )


class DashboardView(LoginRequiredMixin, View):
    """Main dashboard view - role-based rendering."""

    login_url = "accounts:auth"

    def get(self, request):
        user = request.user
        school = School.get_instance()

        # Student dashboard - with exam data
        if user.is_student:
            # Get exams for student's class (via subject)
            student_exams = Exam.objects.filter(
                subject__assigned_class=user.assigned_class,
                status=Exam.Status.PUBLISHED,
                is_active=True,
            ).select_related("subject")
            # Count active exams (currently running)
            active_exams = [e for e in student_exams if e.is_running]
            # Get student's attempts
            attempts = ExamAttempt.objects.filter(student=user)
            completed_attempts = attempts.filter(status=ExamAttempt.Status.SUBMITTED)

            return render(
                request,
                "accounts/dashboard_student.html",
                {
                    "school": school,
                    "user": user,
                    "active_exam_count": len(active_exams),
                    "completed_exam_count": completed_attempts.count(),
                    "total_exam_count": student_exams.count(),
                },
            )

        # Teacher dashboard (coming soon - for now same as student)
        if user.is_teacher:
            return render(
                request,
                "accounts/dashboard_teacher.html",
                {
                    "school": school,
                    "user": user,
                },
            )

        # Examiner dashboard
        if user.is_examiner:
            return render(
                request,
                "accounts/dashboard_examiner.html",
                {
                    "school": school,
                    "user": user,
                    "question_count": Question.objects.filter(
                        created_by=user, is_active=True
                    ).count(),
                    "exam_count": Exam.objects.filter(
                        created_by=user, is_active=True
                    ).count(),
                },
            )

        # Admin dashboard - full view
        context = {
            "school": school,
            "user": user,
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
        return render(request, "accounts/dashboard.html", context)


class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin that requires admin role."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)


class ExaminerManagementView(AdminRequiredMixin, View):
    """Examiner management view."""

    template_name = "accounts/users/examiners.html"

    def get(self, request):
        context = {
            "users": User.objects.filter(role=User.Role.EXAMINER).order_by(
                "first_name", "last_name"
            ),
            "form": AddExaminerForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get("action")
        if action == "add":
            form = AddExaminerForm(request.POST)
            if form.is_valid():
                # Create invitation instead of user
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.EXAMINER,
                    invited_by=request.user,
                )
                # Send invite email
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                send_mail(
                    subject="ExamCore - You've been invited",
                    message=f"Hi {invitation.first_name},\n\n"
                    f"You've been invited to join ExamCore as an Examiner.\n\n"
                    f"Click here to set your password and activate your account:\n{invite_url}\n\n"
                    f"This link expires in 7 days.",
                    from_email="noreply@examcore.local",
                    recipient_list=[invitation.email],
                    fail_silently=False,
                )
                messages.success(request, f"Invitation sent to {invitation.email}")
                return redirect("accounts:examiners")
            context = {
                "users": User.objects.filter(role=User.Role.EXAMINER).order_by(
                    "first_name", "last_name"
                ),
                "form": form,
                "show_modal": True,
            }
            return render(request, self.template_name, context)
        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            try:
                user = User.objects.get(id=user_id)
                user.is_active = not user.is_active
                user.save()
                status = "activated" if user.is_active else "deactivated"
                messages.success(
                    request, f"Examiner '{user.get_full_name()}' {status}."
                )
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect("accounts:examiners")


class TeacherManagementView(AdminRequiredMixin, View):
    """Teacher management view."""

    template_name = "accounts/users/teachers.html"

    def get(self, request):
        context = {
            "users": User.objects.filter(role=User.Role.TEACHER).order_by(
                "first_name", "last_name"
            ),
            "form": AddTeacherForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get("action")
        if action == "add":
            form = AddTeacherForm(request.POST)
            if form.is_valid():
                # Create invitation instead of user
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.TEACHER,
                    invited_by=request.user,
                )
                # Send invite email
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                send_mail(
                    subject="ExamCore - You've been invited",
                    message=f"Hi {invitation.first_name},\n\n"
                    f"You've been invited to join ExamCore as a Teacher.\n\n"
                    f"Click here to set your password and activate your account:\n{invite_url}\n\n"
                    f"This link expires in 7 days.",
                    from_email="noreply@examcore.local",
                    recipient_list=[invitation.email],
                    fail_silently=False,
                )
                messages.success(request, f"Invitation sent to {invitation.email}")
                return redirect("accounts:teachers")
            context = {
                "users": User.objects.filter(role=User.Role.TEACHER).order_by(
                    "first_name", "last_name"
                ),
                "form": form,
                "show_modal": True,
            }
            return render(request, self.template_name, context)
        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            try:
                user = User.objects.get(id=user_id)
                user.is_active = not user.is_active
                user.save()
                status = "activated" if user.is_active else "deactivated"
                messages.success(request, f"Teacher '{user.get_full_name()}' {status}.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect("accounts:teachers")


class StudentManagementView(AdminRequiredMixin, View):
    """Student management view - filtered by class."""

    template_name = "accounts/users/students.html"

    def get_class(self, class_id):
        """Get the selected class from URL path."""
        try:
            return Class.objects.get(id=class_id, is_active=True)
        except Class.DoesNotExist:
            return None

    def get(self, request, class_id):
        selected_class = self.get_class(class_id)
        if not selected_class:
            messages.warning(request, "Class not found.")
            return redirect("accounts:classes")

        context = {
            "selected_class": selected_class,
            "users": User.objects.filter(
                role=User.Role.STUDENT, assigned_class=selected_class
            ).order_by("first_name", "last_name"),
            "form": AddStudentForm(initial={"assigned_class": selected_class}),
        }
        return render(request, self.template_name, context)

    def post(self, request, class_id):
        selected_class = self.get_class(class_id)
        if not selected_class:
            return redirect("accounts:classes")

        action = request.POST.get("action")
        if action == "add":
            form = AddStudentForm(request.POST)
            if form.is_valid():
                # Create invitation instead of user
                invitation = Invitation.create_invitation(
                    email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    phone=form.cleaned_data["phone"],
                    role=User.Role.STUDENT,
                    invited_by=request.user,
                    assigned_class=form.cleaned_data["assigned_class"],
                )
                # Send invite email
                invite_url = request.build_absolute_uri(invitation.get_invite_url())
                send_mail(
                    subject="ExamCore - You've been invited",
                    message=f"Hi {invitation.first_name},\n\n"
                    f"You've been invited to join ExamCore as a Student in {selected_class.name}.\n\n"
                    f"Click here to set your password and activate your account:\n{invite_url}\n\n"
                    f"This link expires in 7 days.",
                    from_email="noreply@examcore.local",
                    recipient_list=[invitation.email],
                    fail_silently=False,
                )
                messages.success(request, f"Invitation sent to {invitation.email}")
                return redirect("accounts:students", class_id=class_id)
            context = {
                "selected_class": selected_class,
                "users": User.objects.filter(
                    role=User.Role.STUDENT, assigned_class=selected_class
                ).order_by("first_name", "last_name"),
                "form": form,
                "show_modal": True,
            }
            return render(request, self.template_name, context)
        elif action == "toggle_active":
            user_id = request.POST.get("user_id")
            try:
                user = User.objects.get(id=user_id)
                user.is_active = not user.is_active
                user.save()
                status = "activated" if user.is_active else "deactivated"
                messages.success(request, f"Student '{user.get_full_name()}' {status}.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect("accounts:students", class_id=class_id)


class ClassManagementView(AdminRequiredMixin, View):
    """Class management view."""

    template_name = "accounts/classes/management.html"

    def get(self, request):
        context = {
            "classes": Class.objects.all(),
            "form": ClassForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        action = request.POST.get("action")

        if action == "add":
            return self.handle_add_class(request)
        elif action == "reorder":
            return self.handle_reorder(request)

        return redirect("accounts:classes")

    def handle_add_class(self, request):
        """Handle adding a new class."""
        form = ClassForm(request.POST)

        if form.is_valid():
            cls = form.save(commit=False)
            # Auto-increment order
            max_order = Class.objects.aggregate(models.Max("order"))["order__max"] or -1
            cls.order = max_order + 1
            cls.save()
            messages.success(request, f"Class '{cls.name}' added successfully.")
            return redirect("accounts:classes")

        context = {
            "classes": Class.objects.all(),
            "form": form,
            "show_modal": True,
        }
        return render(request, self.template_name, context)

    def handle_reorder(self, request):
        """Handle reordering classes via drag and drop."""
        import json

        order_data = request.POST.get("order", "[]")
        try:
            class_ids = json.loads(order_data)
            for index, class_id in enumerate(class_ids):
                Class.objects.filter(id=class_id).update(order=index)
        except (json.JSONDecodeError, ValueError):
            messages.error(request, "Failed to reorder classes.")

        return redirect("accounts:classes")


class SubjectManagementView(AdminRequiredMixin, View):
    """Subject management view - filtered by class."""

    template_name = "accounts/subjects/management.html"

    def get_class(self, class_id):
        """Get the selected class from URL path."""
        try:
            return Class.objects.get(id=class_id, is_active=True)
        except Class.DoesNotExist:
            return None

    def get(self, request, class_id):
        selected_class = self.get_class(class_id)
        if not selected_class:
            messages.warning(request, "Class not found.")
            return redirect("accounts:classes")

        context = {
            "selected_class": selected_class,
            "subjects": Subject.objects.filter(assigned_class=selected_class),
            "form": SubjectForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request, class_id):
        selected_class = self.get_class(class_id)
        if not selected_class:
            return redirect("accounts:classes")

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
                return redirect("accounts:subjects", class_id=class_id)
            context = {
                "selected_class": selected_class,
                "subjects": Subject.objects.filter(assigned_class=selected_class),
                "form": form,
                "show_modal": True,
            }
            return render(request, self.template_name, context)
        elif action == "toggle_active":
            subject_id = request.POST.get("subject_id")
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.is_active = not subject.is_active
                subject.save()
                status = "activated" if subject.is_active else "deactivated"
                messages.success(request, f"Subject '{subject.name}' {status}.")
            except Subject.DoesNotExist:
                messages.error(request, "Subject not found.")
        return redirect("accounts:subjects", class_id=class_id)
