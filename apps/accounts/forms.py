from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import EmailValidator

from .models import Class, School, User

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Login form with styled fields. Uses email as username."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
        })
    )

    def clean_username(self):
        """Normalize email to lowercase for authentication."""
        username = self.cleaned_data.get('username', '')
        return username.lower()


class RegisterForm(forms.Form):
    """Registration form with email and password."""

    email = forms.EmailField(
        label="Email Address",
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password (min 8 characters)',
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
        })
    )

    def clean_email(self):
        """Normalize email to lowercase and check uniqueness."""
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class VerifyOTPForm(forms.Form):
    """OTP verification form - reusable for email verification and password reset."""

    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input-otp',
            'placeholder': '000000',
            'maxlength': '6',
            'autofocus': True,
            'autocomplete': 'one-time-code',
        })
    )


class SchoolSetupForm(forms.ModelForm):
    """School/College setup form."""

    class Meta:
        model = School
        fields = ['name', 'logo', 'email', 'phone', 'address']
        labels = {
            'name': 'Institution Name',
            'logo': 'Logo',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter school or college name',
                'autofocus': True,
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter institution email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter phone number',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Enter full address',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields required
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['address'].required = True


class ClassForm(forms.ModelForm):
    """Form for creating/editing classes."""

    class Meta:
        model = Class
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter class name',
                'autofocus': True,
            }),
        }


class AddUserForm(forms.ModelForm):
    """Form for inviting users (no password - user sets it themselves via invite link)."""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter email address',
                'autofocus': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone number',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.role = kwargs.pop('role', User.Role.STUDENT)
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True

    def clean_email(self):
        """Normalize email to lowercase and check uniqueness."""
        from .models import Invitation
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        # Check for pending invitations
        if Invitation.objects.filter(email=email, accepted_at__isnull=True).exists():
            raise forms.ValidationError("An invitation has already been sent to this email.")
        return email


class SetPasswordForm(forms.Form):
    """Form for invited users to set their password."""

    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password (min 8 characters)',
            'autofocus': True,
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """Form for requesting password reset."""

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your registered email',
            'autofocus': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("No active account found with this email.")
        return email


class ResetPasswordForm(forms.Form):
    """Form for resetting password with OTP."""

    otp = forms.CharField(
        label="Enter OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input-otp',
            'placeholder': '000000',
            'maxlength': '6',
            'autofocus': True,
            'autocomplete': 'one-time-code',
        })
    )
    password = forms.CharField(
        label="New Password",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a new password (min 8 characters)',
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class AddExaminerForm(AddUserForm):
    """Form for adding examiners."""

    def __init__(self, *args, **kwargs):
        kwargs['role'] = User.Role.EXAMINER
        super().__init__(*args, **kwargs)


class AddTeacherForm(AddUserForm):
    """Form for adding teachers."""

    def __init__(self, *args, **kwargs):
        kwargs['role'] = User.Role.TEACHER
        super().__init__(*args, **kwargs)


class AddStudentForm(AddUserForm):
    """Form for inviting students with class assignment."""

    assigned_class = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        label="Class",
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta(AddUserForm.Meta):
        fields = ['email', 'first_name', 'last_name', 'phone', 'assigned_class']

    def __init__(self, *args, **kwargs):
        kwargs['role'] = User.Role.STUDENT
        super().__init__(*args, **kwargs)
