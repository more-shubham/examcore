from django.contrib import admin

from .models import Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    max_num = 8
    min_num = 4
    fields = ["text"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "question_text_short",
        "subject",
        "correct_option_text",
        "created_by",
        "is_active",
    ]
    list_filter = ["subject", "is_active", "created_by"]
    search_fields = ["question_text"]
    inlines = [QuestionOptionInline]
    raw_id_fields = ["correct_option", "subject", "created_by", "updated_by"]

    def question_text_short(self, obj):
        return (
            obj.question_text[:50] + "..."
            if len(obj.question_text) > 50
            else obj.question_text
        )

    question_text_short.short_description = "Question"

    def correct_option_text(self, obj):
        if obj.correct_option:
            return (
                obj.correct_option.text[:30] + "..."
                if len(obj.correct_option.text) > 30
                else obj.correct_option.text
            )
        return "-"

    correct_option_text.short_description = "Correct Answer"


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ["text_short", "question", "created_at"]
    list_filter = ["question__subject"]
    search_fields = ["text", "question__question_text"]
    raw_id_fields = ["question", "updated_by"]

    def text_short(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_short.short_description = "Option Text"
