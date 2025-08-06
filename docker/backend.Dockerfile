# Multi-stage production-optimized Dockerfile for Digital Greenhouse Backend
# Optimized for security, performance, and minimal attack surface

# ===================================
# Build Stage
# ===================================
FROM python:3.11-slim as builder

# Set build arguments
ARG POETRY_VERSION=1.7.1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Set poetry configuration
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry-cache

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# ===================================
# Production Stage
# ===================================
FROM python:3.11-slim as production

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    ca-certificates \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get autoclean

# Create non-root user
RUN groupadd -r appuser && \
    useradd --no-log-init -r -g appuser appuser && \
    mkdir -p /app /home/appuser && \
    chown -R appuser:appuser /app /home/appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder --chown=appuser:appuser ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Ensure we use venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app

# Install the application
RUN pip install -e . --no-deps

# Copy entrypoint script
COPY docker/scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh && \
    chown appuser:appuser /usr/local/bin/entrypoint.sh

# Copy health check script
COPY docker/scripts/healthcheck.sh /usr/local/bin/healthcheck-backend.sh
RUN chmod +x /usr/local/bin/healthcheck-backend.sh && \
    chown appuser:appuser /usr/local/bin/healthcheck-backend.sh

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKERS=4 \
    WORKER_CLASS=uvicorn.workers.UvicornWorker \
    HOST=0.0.0.0 \
    PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck-backend.sh

# Labels for metadata
LABEL maintainer="Cameron Potter <cameron@example.com>"
LABEL version="1.0.0"
LABEL description="Digital Greenhouse Backend - Production Optimized"
LABEL org.opencontainers.image.source="https://github.com/cameronopotter/digital-greenhouse"

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command
CMD ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000"]