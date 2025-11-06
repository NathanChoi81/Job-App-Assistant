FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Docker client
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

# Copy application code
COPY . .

# Run Celery worker
CMD ["poetry", "run", "celery", "-A", "worker.main", "worker", "--loglevel=info"]

