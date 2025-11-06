# Setup Guide

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- Poetry (for Python dependency management)
- Docker (for local Tectonic compilation testing)
- Supabase account
- Upstash account
- OpenAI API key

### Initial Setup

1. **Clone and install dependencies**

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd apps/frontend
npm install

# Install API dependencies
cd ../api
poetry install

# Install worker dependencies
cd ../worker
poetry install

# Install shared types
cd ../../packages/shared-types
npm install
```

2. **Set up environment variables**

Create `.env` files in each app:

**apps/frontend/.env.local:**
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**apps/api/.env:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
OPENAI_API_KEY=sk-...
REDIS_URL=redis://default:...@...:6379
CELERY_BROKER_URL=redis://default:...@...:6379
ENVIRONMENT=development
```

**apps/worker/.env:**
```
REDIS_URL=redis://default:...@...:6379
CELERY_BROKER_URL=redis://default:...@...:6379
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
ENVIRONMENT=development
```

3. **Set up Supabase**

- Run the SQL migration from `infra/supabase/schema.sql`
- Create a storage bucket named `resumes` with public access

4. **Install spaCy model**

```bash
cd apps/api
poetry run python -m spacy download en_core_web_sm
```

5. **Run database migrations**

```bash
cd apps/api
poetry run alembic upgrade head
```

### Running Locally

**Terminal 1 - Frontend:**
```bash
cd apps/frontend
npm run dev
```

**Terminal 2 - API:**
```bash
cd apps/api
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Worker:**
```bash
cd apps/worker
poetry run celery -A worker.main worker --loglevel=info
```

**Terminal 4 - Redis (if running locally):**
```bash
redis-server
```

### Testing

**Frontend:**
```bash
cd apps/frontend
npm run test  # If you add tests
```

**API:**
```bash
cd apps/api
poetry run pytest
```

## Project Structure

```
/
├── apps/
│   ├── frontend/          # Next.js 15 app
│   ├── api/               # FastAPI backend
│   └── worker/            # Celery worker
├── packages/
│   └── shared-types/      # Shared TypeScript types
├── infra/
│   └── supabase/          # Database schema
└── .github/
    └── workflows/         # CI/CD pipelines
```

## Key Features

- ✅ Master Resume upload and parsing (LaTeX)
- ✅ JD analysis with AI-powered skill extraction
- ✅ Resume tailoring with drag-and-drop skill ordering
- ✅ Cover letter generation
- ✅ Job application tracking
- ✅ Outreach contact management
- ✅ PDF compilation via Tectonic (Docker sandbox)
- ✅ Free-tier friendly architecture

## Next Steps

1. Review the codebase
2. Set up your services (Supabase, Upstash, etc.)
3. Configure environment variables
4. Run locally and test
5. Deploy to production (see DEPLOYMENT.md)

