from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from .forms import SetPasswordForm
from .models import Invitation

User = get_user_model()


class AcceptInviteView(View):
    """Accept invitation and set password."""

    template_name = "invitations/accept_invite.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboards:home")
        return super().dispatch(request, *args, **kwargs)

    def get_invitation(self, token):
        invitation = get_object_or_404(Invitation, token=token)
        if not invitation.is_valid():
            return None
        return invitation

    def get(self, request, token):
        invitation = self.get_invitation(token)
        if not invitation:
            messages.error(request, "This invitation has expired or is invalid.")
            return redirect("auth:login")

        form = SetPasswordForm()
        return render(
            request,
            self.template_name,
            {
                "invitation": invitation,
                "form": form,
            },
        )

    def post(self, request, token):
        invitation = self.get_invitation(token)
        if not invitation:
            messages.error(request, "This invitation has expired or is invalid.")
            return redirect("auth:login")

        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Create user from invitation
            user = User.objects.create_user(
                username=invitation.email,
                email=invitation.email,
                password=form.cleaned_data["password"],
                first_name=invitation.first_name,
                last_name=invitation.last_name,
                phone=invitation.phone,
                role=invitation.role,
                assigned_class=invitation.assigned_class,
            )

            # Mark invitation as accepted
            invitation.accepted_at = timezone.now()
            invitation.save()

            # Log in the user
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect("dashboards:home")

        return render(
            request,
            self.template_name,
            {
                "invitation": invitation,
                "form": form,
            },
        )
