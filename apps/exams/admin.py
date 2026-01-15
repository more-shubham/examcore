from django.contrib import admin

from .models import Exam, ExamQuestion


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "status",
        "start_time",
        "end_time",
        "created_by",
    ]
    list_filter = ["status", "subject", "is_active"]
    search_fields = ["title", "description"]
    date_hierarchy = "start_time"


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ["exam", "question", "order"]
    list_filter = ["exam"]
