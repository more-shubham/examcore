from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "question_text_short",
        "subject",
        "correct_option",
        "created_by",
        "is_active",
    ]
    list_filter = ["subject", "is_active", "created_by"]
    search_fields = ["question_text"]

    def question_text_short(self, obj):
        return (
            obj.question_text[:50] + "..."
            if len(obj.question_text) > 50
            else obj.question_text
        )

    question_text_short.short_description = "Question"
