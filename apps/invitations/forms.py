from django import forms


class SetPasswordForm(forms.Form):
    """Form for invited users to set their password."""

    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Create a password (min 8 characters)",
                "autofocus": True,
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

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
