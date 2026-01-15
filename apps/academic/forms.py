from django import forms

from .models import Class, Subject


class ClassForm(forms.ModelForm):
    """Form for creating/editing classes."""

    class Meta:
        model = Class
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter class name",
                    "autofocus": True,
                }
            ),
        }


class SubjectForm(forms.ModelForm):
    """Form for creating/editing subjects."""

    class Meta:
        model = Subject
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter subject name (e.g., Mathematics)",
                    "autofocus": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": "Optional description",
                    "rows": 2,
                }
            ),
        }
