from django import forms

from apps.accounts.models import Class

from .models import Exam


class ExamForm(forms.ModelForm):
    """Form for creating/editing exams."""

    class Meta:
        model = Exam
        fields = [
            "title",
            "description",
            "assigned_class",
            "start_time",
            "end_time",
            "use_random_questions",
            "random_question_count",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter exam title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": "Optional description",
                }
            ),
            "assigned_class": forms.Select(attrs={"class": "form-input"}),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-input",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "class": "form-input",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "use_random_questions": forms.CheckboxInput(
                attrs={"class": "form-checkbox"}
            ),
            "random_question_count": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "min": 1,
                    "placeholder": "Number of questions",
                }
            ),
            "status": forms.Select(attrs={"class": "form-input"}),
        }
        labels = {
            "use_random_questions": "Random question selection",
            "random_question_count": "Number of questions",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_class"].queryset = Class.objects.filter(is_active=True)

        # Format datetime fields for editing
        if self.instance.pk:
            if self.instance.start_time:
                self.initial["start_time"] = self.instance.start_time.strftime(
                    "%Y-%m-%dT%H:%M"
                )
            if self.instance.end_time:
                self.initial["end_time"] = self.instance.end_time.strftime(
                    "%Y-%m-%dT%H:%M"
                )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        use_random = cleaned_data.get("use_random_questions")
        question_count = cleaned_data.get("random_question_count")

        # Validate timing
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                "End time must be after start time.",
                code="invalid_time_range",
            )

        # Validate random question count
        if use_random and (not question_count or question_count < 1):
            self.add_error(
                "random_question_count",
                "Please specify how many questions to include.",
            )

        return cleaned_data
