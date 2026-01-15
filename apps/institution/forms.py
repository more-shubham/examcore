from django import forms

from .models import Institution


class InstitutionSetupForm(forms.ModelForm):
    """Institution (School/College/University) setup form."""

    class Meta:
        model = Institution
        fields = ["name", "logo", "email", "phone", "address"]
        labels = {
            "name": "Institution Name",
            "logo": "Logo",
            "email": "Email",
            "phone": "Phone",
            "address": "Address",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter institution name (school, college, university)",
                    "autofocus": True,
                }
            ),
            "logo": forms.FileInput(
                attrs={
                    "class": "form-input-file",
                    "accept": "image/*",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter institution email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter phone number",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": "Enter full address",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["phone"].required = True
        self.fields["address"].required = True
