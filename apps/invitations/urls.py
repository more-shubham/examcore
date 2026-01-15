from django.urls import path

from . import views

app_name = "invitations"

urlpatterns = [
    path("invite/<str:token>/", views.AcceptInviteView.as_view(), name="accept"),
]
