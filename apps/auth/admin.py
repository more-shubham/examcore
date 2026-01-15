from django.contrib import admin

from .models import OTPVerification


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("email", "is_verified", "created_at", "expires_at")
    list_filter = ("is_verified",)
    search_fields = ("email",)
    readonly_fields = ("otp", "created_at", "updated_at")
