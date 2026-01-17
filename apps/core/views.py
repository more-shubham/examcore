import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    def get(self, request):
        health_status = {
            "status": "healthy",
            "database": "ok",
        }
        status_code = 200

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError as e:
            logger.error(f"Health check failed - Database error: {e}")
            health_status["status"] = "unhealthy"
            health_status["database"] = "error"
            status_code = 503

        return JsonResponse(health_status, status=status_code)


class ReadinessCheckView(View):
    def get(self, request):
        readiness_status = {
            "status": "ready",
            "database": "ok",
            "cache": "ok",
        }
        status_code = 200

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError as e:
            logger.error(f"Readiness check failed - Database error: {e}")
            readiness_status["status"] = "not_ready"
            readiness_status["database"] = "error"
            status_code = 503

        try:
            from django.core.cache import cache

            cache.set("readiness_check", "ok", 10)
            if cache.get("readiness_check") != "ok":
                raise ValueError("Cache read/write failed")
        except (DatabaseError, ValueError) as e:
            logger.error(f"Readiness check failed - Cache error: {e}")
            readiness_status["status"] = "not_ready"
            readiness_status["cache"] = "error"
            status_code = 503

        return JsonResponse(readiness_status, status=status_code)


class LivenessCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "alive"})
