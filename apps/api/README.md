# API Backend

FastAPI backend for the Smart Resume & Cover Letter Generator.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Download spaCy model:
```bash
poetry run python -m spacy download en_core_web_sm
```

3. Set environment variables (see `.env.example`)

4. Run migrations:
```bash
poetry run alembic upgrade head
```

5. Start server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT secret for token verification
- `OPENAI_API_KEY` - OpenAI API key
- `REDIS_URL` - Upstash Redis URL
- `CELERY_BROKER_URL` - Redis broker URL (same as REDIS_URL)
- `SENTRY_DSN` - Sentry DSN (optional)
- `ENVIRONMENT` - `development` or `production`

