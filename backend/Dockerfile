FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    netcat-traditional \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure poetry to not use a virtual environment in Docker
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock* (if exists)
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-interaction

# Code will be mounted via docker-compose volume
# No need to COPY . . here!

# Expose port for the application
EXPOSE 8000