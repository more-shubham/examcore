from django.contrib import admin

from .models import ExamAnswer, ExamAttempt


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam",
        "status",
        "score",
        "total_questions",
        "started_at",
    )
    list_filter = ("status", "exam")
    search_fields = ("student__email", "exam__title")
    readonly_fields = ("question_order", "option_orders", "created_at", "updated_at")


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_option", "is_correct")
    list_filter = ("is_correct",)
