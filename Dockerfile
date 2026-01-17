# =============================================================================
# ExamCore Production Dockerfile
# =============================================================================

FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Builder stage - install dependencies
# =============================================================================

FROM base AS builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Production stage
# =============================================================================

FROM base AS production

# Create non-root user for security
RUN groupadd --gid 1000 examcore \
    && useradd --uid 1000 --gid examcore --shell /bin/bash --create-home examcore

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=examcore:examcore . .

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R examcore:examcore /app/staticfiles /app/media

# Switch to non-root user
USER examcore

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command (override in docker-compose for development)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread"]
