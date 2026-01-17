"""URL configuration for ExamCore project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Health checks (no auth required)
    path("", include("apps.core.urls", namespace="core")),
    # Admin
    path("admin/", admin.site.urls),
    # Dashboard
    path("dashboard/", include("apps.dashboards.urls", namespace="dashboards")),
    # Question bank
    path("questions/", include("apps.questions.urls", namespace="questions")),
    # Exam management (admin/examiner)
    path("exams/", include("apps.exams.urls", namespace="exams")),
    # Student exam attempts
    path("my-exams/", include("apps.attempts.urls", namespace="attempts")),
    # Invitations (accept invite) - /invite/<token>/
    path("", include("apps.invitations.urls", namespace="invitations")),
    # Academic management (classes, subjects)
    path("", include("apps.academic.urls", namespace="academic")),
    # User management (examiners, teachers, students)
    path("", include("apps.users.urls", namespace="users")),
    # Authentication (root URL - login/register)
    path("", include("apps.auth.urls", namespace="auth")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
