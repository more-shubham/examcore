from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.views import View

from apps.core.services.email import EmailService
from apps.institution.forms import InstitutionSetupForm

from .forms import (
    ForgotPasswordForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
    VerifyOTPForm,
)
from .models import OTPVerification

User = get_user_model()


class AuthView(View):
    """Single-page authentication with multi-step registration."""

    template_name = "auth/auth.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)

    def get_mode(self, request):
        """Determine which form to show."""
        if request.session.get("otp_verified"):
            return "institution"
        if request.session.get("pending_email"):
            return "verify"
        if User.objects.filter(role=User.Role.ADMIN).exists():
            return "login"
        return "register"

    def get_context(self, request, mode, form=None):
        forms_map = {
            "login": LoginForm,
            "register": RegisterForm,
            "verify": VerifyOTPForm,
            "institution": InstitutionSetupForm,
        }

        return {
            "mode": mode,
            "form": form or forms_map[mode](),
            "pending_email": request.session.get("pending_email"),
        }

    def get(self, request):
        mode = self.get_mode(request)
        return render(request, self.template_name, self.get_context(request, mode))

    def post(self, request):
        mode = self.get_mode(request)

        if mode == "login":
            return self.handle_login(request)
        elif mode == "register":
            return self.handle_register(request)
        elif mode == "verify":
            return self.handle_verify(request)
        elif mode == "institution":
            return self.handle_institution(request)

        return redirect("auth:login")

    def handle_login(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().first_name}!")
            return redirect("dashboards:home")
        return render(
            request, self.template_name, self.get_context(request, "login", form)
        )

    def handle_register(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp_obj = OTPVerification.generate_otp(email)

            if EmailService.send_otp_email(email, otp_obj.otp):
                request.session["pending_email"] = email
                request.session["pending_password"] = form.cleaned_data["password"]
                messages.info(request, "Verification code sent to your email.")
            else:
                messages.error(
                    request, "Failed to send verification email. Please try again."
                )
            return redirect("auth:login")
        return render(
            request, self.template_name, self.get_context(request, "register", form)
        )

    def handle_verify(self, request):
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            email = request.session.get("pending_email")
            if OTPVerification.verify(email, form.cleaned_data["otp"]):
                request.session["otp_verified"] = True
                messages.success(
                    request, "Email verified! Now set up your institution."
                )
                return redirect("auth:login")
            form.add_error("otp", "Invalid or expired OTP.")
        return render(
            request, self.template_name, self.get_context(request, "verify", form)
        )

    def handle_institution(self, request):
        form = InstitutionSetupForm(request.POST, request.FILES)
        if form.is_valid():
            institution = form.save()

            # Create admin user
            user = User.objects.create_user(
                username=request.session["pending_email"],
                email=request.session["pending_email"],
                password=request.session["pending_password"],
                role=User.Role.ADMIN,
            )

            # Clear session
            for key in ["pending_email", "pending_password", "otp_verified"]:
                request.session.pop(key, None)

            login(request, user)
            messages.success(request, f"Welcome to {institution.name}!")
            return redirect("dashboards:home")
        return render(
            request, self.template_name, self.get_context(request, "institution", form)
        )


class CustomLogoutView(LogoutView):
    """Custom logout redirecting to home."""

    next_page = "auth:login"


class ResendOTPView(View):
    """Resend OTP for email verification."""

    def post(self, request):
        email = request.session.get("pending_email")
        if email:
            otp_obj = OTPVerification.generate_otp(email)
            if EmailService.send_otp_email(email, otp_obj.otp):
                messages.info(request, "New verification code sent.")
            else:
                messages.error(
                    request, "Failed to send verification email. Please try again."
                )
        else:
            messages.error(request, "Session expired. Please start registration again.")
        return redirect("auth:login")


class ForgotPasswordView(View):
    """Request password reset."""

    template_name = "auth/forgot_password.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": ForgotPasswordForm()})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp_obj = OTPVerification.generate_otp(email)
            if EmailService.send_password_reset_email(email, otp_obj.otp):
                request.session["reset_email"] = email
                messages.info(request, "Password reset code sent to your email.")
                return redirect("auth:reset_password")
            else:
                messages.error(request, "Failed to send reset email. Please try again.")
        return render(request, self.template_name, {"form": form})


class ResetPasswordView(View):
    """Reset password with OTP."""

    template_name = "auth/reset_password.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboards:home")
        if not request.session.get("reset_email"):
            return redirect("auth:forgot_password")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "form": ResetPasswordForm(),
                "email": request.session.get("reset_email"),
            },
        )

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = request.session.get("reset_email")
            if OTPVerification.verify(email, form.cleaned_data["otp"]):
                user = User.objects.get(email=email)
                user.set_password(form.cleaned_data["password"])
                user.save()
                request.session.pop("reset_email", None)
                messages.success(request, "Password reset successfully. Please log in.")
                return redirect("auth:login")
            form.add_error("otp", "Invalid or expired OTP.")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "email": request.session.get("reset_email"),
            },
        )
