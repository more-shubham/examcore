from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import EmailValidator

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Login form with email as username."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your password",
            }
        ),
    )

    def clean_username(self):
        return self.cleaned_data.get("username", "").lower()


class RegisterForm(forms.Form):
    """Registration form for first admin."""

    email = forms.EmailField(
        label="Email Address",
        validators=[EmailValidator()],
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your email address",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a password (min 8 characters)",
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Confirm your password",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class VerifyOTPForm(forms.Form):
    """OTP verification form."""

    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-input-otp",
                "placeholder": "000000",
                "maxlength": "6",
                "autofocus": True,
                "autocomplete": "one-time-code",
            }
        ),
    )


class ForgotPasswordForm(forms.Form):
    """Form for requesting password reset."""

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter your registered email",
                "autofocus": True,
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("No active account found with this email.")
        return email


class ResetPasswordForm(forms.Form):
    """Form for resetting password with OTP."""

    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-input-otp",
                "placeholder": "000000",
                "maxlength": "6",
                "autofocus": True,
                "autocomplete": "one-time-code",
            }
        ),
    )
    password = forms.CharField(
        label="New Password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a new password (min 8 characters)",
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Confirm your new password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
