from django import forms
from django.contrib.auth import get_user_model

from apps.academic.models import Class

User = get_user_model()


class AddUserForm(forms.ModelForm):
    """Base form for inviting users."""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter email address",
                    "autofocus": True,
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Last name",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Phone number",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.role = kwargs.pop("role", User.Role.STUDENT)
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["phone"].required = True

    def clean_email(self):
        from apps.invitations.models import Invitation

        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if Invitation.objects.filter(email=email, accepted_at__isnull=True).exists():
            raise forms.ValidationError(
                "An invitation has already been sent to this email."
            )
        return email


class AddExaminerForm(AddUserForm):
    """Form for adding examiners."""

    def __init__(self, *args, **kwargs):
        kwargs["role"] = User.Role.EXAMINER
        super().__init__(*args, **kwargs)


class AddTeacherForm(AddUserForm):
    """Form for adding teachers."""

    def __init__(self, *args, **kwargs):
        kwargs["role"] = User.Role.TEACHER
        super().__init__(*args, **kwargs)


class AddStudentForm(AddUserForm):
    """Form for inviting students with class assignment."""

    assigned_class = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),
        label="Class",
        required=True,
        widget=forms.HiddenInput(),
    )

    class Meta(AddUserForm.Meta):
        fields = ["email", "first_name", "last_name", "phone", "assigned_class"]

    def __init__(self, *args, **kwargs):
        kwargs["role"] = User.Role.STUDENT
        super().__init__(*args, **kwargs)
