from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("", views.AuthView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("resend-otp/", views.ResendOTPView.as_view(), name="resend_otp"),
    path(
        "forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
]
