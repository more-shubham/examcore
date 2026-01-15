import secrets
from datetime import timedelta

from django.utils import timezone


class OTPService:
    """Service for OTP generation and verification."""

    OTP_EXPIRY_MINUTES = 10

    @staticmethod
    def generate_otp() -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return "".join(secrets.choice("0123456789") for _ in range(6))

    @staticmethod
    def get_expiry_time() -> timezone.datetime:
        """Get OTP expiry timestamp."""
        return timezone.now() + timedelta(minutes=OTPService.OTP_EXPIRY_MINUTES)

    @staticmethod
    def is_expired(expiry_time) -> bool:
        """Check if OTP has expired."""
        return timezone.now() > expiry_time
