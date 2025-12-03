# ============================================================
# Multi-Stage Production Dockerfile
# Portfolio Monte Carlo Analysis Platform
# ============================================================

# ============================================================
# Stage 1: Builder - Install dependencies and compile
# ============================================================
FROM python:3.12-slim AS builder

LABEL maintainer="Salem Investment Counselors"
LABEL description="Portfolio Analysis Platform - Builder Stage"

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt /tmp/
WORKDIR /tmp

# Install Python dependencies
# Use --no-cache-dir to reduce image size
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # Install production-grade dependencies
    pip install --no-cache-dir \
        gunicorn==21.2.0 \
        python-json-logger==2.0.7 \
        prometheus-client==0.19.0 \
        python-dotenv==1.0.0 \
        redis==5.0.1 \
        psycopg2-binary==2.9.9 \
        sentry-sdk==1.39.1

# ============================================================
# Stage 2: Runtime - Production-ready minimal image
# ============================================================
FROM python:3.12-slim AS runtime

LABEL maintainer="Salem Investment Counselors"
LABEL description="Portfolio Analysis Platform - Production"
LABEL version="1.0.0"

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PATH="/opt/venv/bin:$PATH" \
    # Application configuration
    APP_ENV=production \
    LOG_LEVEL=INFO \
    ENABLE_METRICS=true \
    # FastAPI configuration
    API_PORT=8000 \
    API_HOST=0.0.0.0

# Install runtime dependencies only (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for health checks
    curl \
    # Required for some Python packages
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
# UID 1000 is standard for non-root containers
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser -m -s /sbin/nologin appuser && \
    mkdir -p /app /app/audit_logs && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy backend application code
COPY --chown=appuser:appuser backend/ ./backend/

# Create health check script for FastAPI
COPY --chown=appuser:appuser <<'EOF' /app/healthcheck.py
#!/usr/bin/env python3
"""Health check script for container orchestration."""
import sys
import urllib.request
import urllib.error

def check_health():
    """Check if FastAPI application is healthy."""
    try:
        with urllib.request.urlopen('http://localhost:8000/api/health', timeout=2) as response:
            if response.status == 200:
                return 0
            return 1
    except (urllib.error.URLError, TimeoutError):
        return 1

if __name__ == '__main__':
    sys.exit(check_health())
EOF

RUN chmod +x /app/healthcheck.py

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Health check configuration
# Check every 30s, timeout after 3s, start after 30s, allow 3 retries
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# Add metadata labels
LABEL org.opencontainers.image.title="Portfolio Monte Carlo Analysis - FastAPI Backend"
LABEL org.opencontainers.image.description="AI-powered retirement portfolio analysis platform - REST API"
LABEL org.opencontainers.image.vendor="Salem Investment Counselors"
LABEL org.opencontainers.image.source="https://github.com/cooptaylor1-rgb/portfolio-monte-carlo-app"

# Set entrypoint and command for FastAPI with uvicorn
WORKDIR /app/backend
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]

# ============================================================
# Build Instructions:
# 
# Development build:
#   docker build -t portfolio-analyzer:dev .
#
# Production build with version tag:
#   docker build -t portfolio-analyzer:2.0.0 \
#                -t portfolio-analyzer:latest .
#
# Build with build args:
#   docker build --build-arg APP_VERSION=2.0.0 \
#                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#                -t portfolio-analyzer:2.0.0 .
#
# Run container:
#   docker run -p 8000:8000 \
#              -e APP_ENV=production \
#              -e LOG_LEVEL=INFO \
#              portfolio-analyzer:latest
#
# Security scan:
#   docker scan portfolio-analyzer:latest
#
# Image size check:
#   docker images portfolio-analyzer:latest
# ============================================================
