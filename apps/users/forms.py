from django import forms
from django.contrib.auth import get_user_model

from apps.academic.models import Class, Subject

from .models import NotificationPreference

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
    """Form for adding teachers with subject assignment."""

    assigned_subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        label="Assigned Subjects",
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-checkbox",
            }
        ),
        help_text="Select subjects this teacher will teach",
    )

    class Meta(AddUserForm.Meta):
        fields = ["email", "first_name", "last_name", "phone", "assigned_subjects"]

    def __init__(self, *args, **kwargs):
        kwargs["role"] = User.Role.TEACHER
        super().__init__(*args, **kwargs)
        # Group subjects by class for better display
        self.fields["assigned_subjects"].queryset = (
            Subject.objects.filter(is_active=True)
            .select_related("assigned_class")
            .order_by("assigned_class__order", "name")
        )


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


class ProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar"]
        widgets = {
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
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-input",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            # Remove common formatting characters for validation
            digits_only = "".join(c for c in phone if c.isdigit())
            if len(digits_only) < 10:
                raise forms.ValidationError(
                    "Please enter a valid phone number with at least 10 digits."
                )
        return phone


class NotificationPreferencesForm(forms.ModelForm):
    """Form for managing notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = ["exam_published", "exam_reminder", "result_available"]
        widgets = {
            "exam_published": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-primary-600",
                }
            ),
            "exam_reminder": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-primary-600",
                }
            ),
            "result_available": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox h-5 w-5 text-primary-600",
                }
            ),
        }
        labels = {
            "exam_published": "New Exam Notifications",
            "exam_reminder": "Exam Reminders",
            "result_available": "Result Notifications",
        }
        help_texts = {
            "exam_published": "Receive an email when a new exam is published for your class",
            "exam_reminder": "Receive a reminder email 24 hours before an exam starts",
            "result_available": "Receive an email when your exam result is available",
        }
