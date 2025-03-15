ARG PYTHON_VERSION=3.11-slim-bullseye

# Build stage for dependencies
FROM python:${PYTHON_VERSION} AS builder
    WORKDIR /build

    # Install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/*

    RUN pip install --no-cache-dir poetry==2.1.1 poetry-plugin-export==1.9.0

    # Copy dependency files first (better caching)
    COPY pyproject.toml poetry.lock ./

    # Export dependencies to requirements.txt
    RUN poetry config virtualenvs.create false \
        && poetry export --without-hashes --format=requirements.txt --output requirements.txt

# Final stage with minimal footprint
FROM python:${PYTHON_VERSION} AS app

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1

    # Create non-root user
    RUN useradd --user-group --system --no-log-init --create-home appuser

    # Install runtime dependencies only (not build tools)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        && rm -rf /var/lib/apt/lists/*

    WORKDIR /app

    # Copy requirements from builder stage
    COPY --chown=appuser:appuser --from=builder /build/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy application code with proper ownership in one step
    COPY --chown=appuser:appuser ./app ./app

    USER appuser

    # Add healthcheck
    HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
        CMD curl -f http://localhost:8080/health || exit 1

    # Add metadata
    LABEL org.opencontainers.image.source="https://github.com/peacefulseeker/fastapi-url-shortener" \
        org.opencontainers.image.version="1.0.0" \
        org.opencontainers.image.description="URL Shortener Service" \
        org.opencontainers.image.licenses="MIT"

    EXPOSE 8080

    CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8080"]




