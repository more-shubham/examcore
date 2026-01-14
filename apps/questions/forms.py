from django import forms

from apps.accounts.models import Class

from .models import Question


class QuestionForm(forms.ModelForm):
    """Form for creating/editing MCQ questions."""

    class Meta:
        model = Question
        fields = [
            "assigned_class",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
        ]
        widgets = {
            "assigned_class": forms.Select(attrs={"class": "form-input"}),
            "question_text": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": "Enter the question",
                }
            ),
            "option_a": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Option A"}
            ),
            "option_b": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Option B"}
            ),
            "option_c": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Option C"}
            ),
            "option_d": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Option D"}
            ),
            "correct_option": forms.RadioSelect(),
        }
        labels = {
            "assigned_class": "Class",
            "question_text": "Question",
            "option_a": "Option A",
            "option_b": "Option B",
            "option_c": "Option C",
            "option_d": "Option D",
            "correct_option": "Correct Answer",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_class"].queryset = Class.objects.filter(is_active=True)
        self.fields["assigned_class"].empty_label = "Select a class"
