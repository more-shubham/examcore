from django.contrib import admin

from .models import Class, Subject


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active", "student_count")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("order",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "assigned_class", "is_active")
    list_filter = ("is_active", "assigned_class")
    search_fields = ("name",)
