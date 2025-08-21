FROM python:3.12.4-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.2

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main

# Copy application code
COPY . .

# Install the package in editable mode
RUN python -m pip install --no-cache-dir --editable .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "alphaloop_core.api:app", "--host", "0.0.0.0", "--port", "8000"]
