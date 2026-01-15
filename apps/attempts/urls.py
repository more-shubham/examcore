from django.urls import path

from . import views

app_name = "attempts"

urlpatterns = [
    path("", views.StudentExamListView.as_view(), name="list"),
    path("<int:pk>/start/", views.StudentStartExamView.as_view(), name="start"),
    path("<int:pk>/take/", views.StudentExamView.as_view(), name="take"),
    path("<int:pk>/submit/", views.StudentSubmitExamView.as_view(), name="submit"),
    path("<int:pk>/result/", views.StudentResultView.as_view(), name="result"),
]
