"""Core URL patterns including health checks."""

from django.urls import path

from .views import HealthCheckView, LivenessCheckView, ReadinessCheckView

app_name = "core"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("health/ready/", ReadinessCheckView.as_view(), name="readiness"),
    path("health/live/", LivenessCheckView.as_view(), name="liveness"),
]
