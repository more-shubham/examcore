from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path("", views.QuestionBankView.as_view(), name="list"),
    path("add/", views.QuestionCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.QuestionUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="delete"),
]
