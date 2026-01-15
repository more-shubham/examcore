from django.urls import path

from . import views

app_name = "exams"

urlpatterns = [
    # Admin/Examiner URLs
    path("", views.ExamListView.as_view(), name="list"),
    path("add/", views.ExamCreateView.as_view(), name="add"),
    path("<int:pk>/", views.ExamDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ExamUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ExamDeleteView.as_view(), name="delete"),
    path("<int:pk>/questions/", views.ExamQuestionsView.as_view(), name="questions"),
]
