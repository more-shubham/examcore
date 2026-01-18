from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/notifications/",
        views.NotificationPreferencesView.as_view(),
        name="notification_preferences",
    ),
    path("examiners/", views.ExaminerManagementView.as_view(), name="examiners"),
    path("teachers/", views.TeacherManagementView.as_view(), name="teachers"),
    path(
        "classes/<int:class_id>/students/",
        views.StudentManagementView.as_view(),
        name="students",
    ),
]
