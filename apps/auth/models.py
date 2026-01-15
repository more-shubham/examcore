from django.db import models

from apps.core.models import TimestampedModel
from apps.core.services.otp import OTPService


class OTPVerification(TimestampedModel):
    """OTP verification for email verification and password reset."""

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "otp_verification"
        verbose_name = "OTP Verification"
        verbose_name_plural = "OTP Verifications"

    def __str__(self):
        return f"OTP for {self.email}"

    @classmethod
    def generate_otp(cls, email):
        """Generate a new OTP for the given email."""
        # Delete any existing OTPs for this email
        cls.objects.filter(email=email.lower()).delete()

        return cls.objects.create(
            email=email.lower(),
            otp=OTPService.generate_otp(),
            expires_at=OTPService.get_expiry_time(),
        )

    def is_valid(self):
        """Check if OTP is still valid."""
        return not self.is_verified and not OTPService.is_expired(self.expires_at)

    @classmethod
    def verify(cls, email, otp):
        """Verify an OTP."""
        try:
            verification = cls.objects.get(email=email.lower(), otp=otp)
            if verification.is_valid():
                verification.is_verified = True
                verification.save()
                return True
        except cls.DoesNotExist:
            pass
        return False
