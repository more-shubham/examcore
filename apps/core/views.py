"""Core views including health checks."""

import logging

from django.db import connection
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    """
    Health check endpoint for load balancers and monitoring.

    Returns 200 OK if the application is healthy.
    Returns 503 Service Unavailable if there are issues.
    """

    def get(self, request):
        health_status = {
            "status": "healthy",
            "database": "ok",
        }
        status_code = 200

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Health check failed - Database error: {e}")
            health_status["status"] = "unhealthy"
            health_status["database"] = "error"
            status_code = 503

        return JsonResponse(health_status, status=status_code)


class ReadinessCheckView(View):
    """
    Readiness check for Kubernetes/container orchestration.

    Returns 200 OK if the application is ready to receive traffic.
    """

    def get(self, request):
        readiness_status = {
            "status": "ready",
            "database": "ok",
            "cache": "ok",
        }
        status_code = 200

        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Readiness check failed - Database error: {e}")
            readiness_status["status"] = "not_ready"
            readiness_status["database"] = "error"
            status_code = 503

        # Check cache
        try:
            from django.core.cache import cache

            cache.set("readiness_check", "ok", 10)
            if cache.get("readiness_check") != "ok":
                raise Exception("Cache read/write failed")
        except Exception as e:
            logger.error(f"Readiness check failed - Cache error: {e}")
            readiness_status["status"] = "not_ready"
            readiness_status["cache"] = "error"
            status_code = 503

        return JsonResponse(readiness_status, status=status_code)


class LivenessCheckView(View):
    """
    Liveness check for Kubernetes/container orchestration.

    Returns 200 OK if the application process is alive.
    This is a minimal check that doesn't verify external dependencies.
    """

    def get(self, request):
        return JsonResponse({"status": "alive"})
