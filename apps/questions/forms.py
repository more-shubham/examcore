from django import forms
from django.forms import inlineformset_factory

from apps.academic.models import Subject

from .models import Question, QuestionOption


class QuestionOptionForm(forms.ModelForm):
    """Form for individual question option."""

    class Meta:
        model = QuestionOption
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter option text",
                }
            ),
        }


# Create formset for options (4-8 options allowed)
QuestionOptionFormSet = inlineformset_factory(
    Question,
    QuestionOption,
    form=QuestionOptionForm,
    min_num=4,
    max_num=8,
    extra=0,
    can_delete=True,
    validate_min=True,
    validate_max=True,
)


class QuestionForm(forms.ModelForm):
    """Form for creating/editing MCQ questions."""

    correct_option_index = forms.IntegerField(
        required=True,
        min_value=0,
        max_value=7,
        widget=forms.HiddenInput(),
        error_messages={"required": "Please select the correct answer."},
    )

    class Meta:
        model = Question
        fields = [
            "subject",
            "question_text",
        ]
        widgets = {
            "subject": forms.Select(attrs={"class": "form-input"}),
            "question_text": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": "Enter the question",
                }
            ),
        }
        labels = {
            "subject": "Subject",
            "question_text": "Question",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].queryset = Subject.objects.filter(
            is_active=True
        ).select_related("assigned_class")
        self.fields["subject"].empty_label = "Select a subject"

        # Pre-populate correct_option_index for editing
        if self.instance and self.instance.pk and self.instance.correct_option:
            options = list(self.instance.options.all())
            for i, option in enumerate(options):
                if option.id == self.instance.correct_option_id:
                    self.fields["correct_option_index"].initial = i
                    break
