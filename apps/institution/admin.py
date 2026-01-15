from django.contrib import admin

from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_active")
    readonly_fields = ("created_at", "updated_at")
