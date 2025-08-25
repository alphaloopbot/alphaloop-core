# Multi-stage build to properly use Poetry
FROM python:3.12-slim as builder

# Install Poetry and build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && pip install poetry

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies (this respects pyproject.toml and poetry.lock)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set Python path to include src directory and infrastructure modules
ENV PYTHONPATH=/app/src:/app/src/infrastructure

# No build tools needed at runtime; keep the image slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psutil; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "alphaloop_core.services.market_data"]
