from django.urls import path

from . import views

app_name = "academic"

urlpatterns = [
    path("classes/", views.ClassManagementView.as_view(), name="classes"),
    path(
        "classes/<int:class_id>/subjects/",
        views.SubjectManagementView.as_view(),
        name="subjects",
    ),
]
