FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including PostgreSQL dev for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Tectonic (LaTeX compiler)
RUN curl -L https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.14.1/tectonic-0.14.1-x86_64-unknown-linux-musl.tar.gz -o /tmp/tectonic.tar.gz \
    && tar -xzf /tmp/tectonic.tar.gz -C /tmp \
    && find /tmp -name "tectonic" -type f -executable -exec mv {} /usr/local/bin/ \; \
    && chmod +x /usr/local/bin/tectonic \
    && rm -rf /tmp/tectonic.tar.gz /tmp/tectonic-*

# Install Poetry
RUN pip install poetry

# Copy dependency files and README (needed for Poetry package installation)
COPY pyproject.toml poetry.lock* README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction

# Copy application code
COPY . .

# Run Celery worker
CMD ["poetry", "run", "celery", "-A", "worker.main", "worker", "--loglevel=info"]

