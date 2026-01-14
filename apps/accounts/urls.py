from django.urls import path

from .views import (
    AcceptInviteView,
    AuthView,
    ClassManagementView,
    CustomLogoutView,
    DashboardView,
    ExaminerManagementView,
    ForgotPasswordView,
    ResendOTPView,
    ResetPasswordView,
    StudentManagementView,
    TeacherManagementView,
)

app_name = 'accounts'

urlpatterns = [
    # Single-page authentication (all forms at /)
    path('', AuthView.as_view(), name='auth'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('invite/<str:token>/', AcceptInviteView.as_view(), name='accept_invite'),

    # Protected pages
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Management (admin only)
    path('examiners/', ExaminerManagementView.as_view(), name='examiners'),
    path('teachers/', TeacherManagementView.as_view(), name='teachers'),
    path('classes/', ClassManagementView.as_view(), name='classes'),
    path('classes/<int:class_id>/students/', StudentManagementView.as_view(), name='students'),
]
