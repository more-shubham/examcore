from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "invited_by", "created_at", "accepted_at")
    list_filter = ("role", "accepted_at")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("token", "created_at", "updated_at")
