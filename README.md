# Smart Resume & Cover Letter Generator

A web application that automatically tailors resumes and cover letters to job descriptions using AI, while maintaining a single "Master Resume" as the source of truth.

## Architecture

- **Frontend**: Next.js 15 (App Router, TypeScript) on Vercel
- **Backend API**: FastAPI on Fly.io
- **Worker**: Celery + Tectonic (Docker) on Fly.io
- **Database**: Supabase (PostgreSQL + Storage + Auth)
- **Cache/Broker**: Upstash Redis
- **Analytics**: Umami (self-hosted on Vercel)

## Project Structure

```
/
├── apps/
│   ├── frontend/      # Next.js application
│   ├── api/           # FastAPI backend
│   └── worker/        # Celery worker with Tectonic
├── packages/
│   ├── shared-types/  # Shared TypeScript/Python types
│   └── ui/            # Shared UI components (optional)
├── infra/
│   ├── docker/        # Dockerfiles
│   ├── fly/           # Fly.io configs
│   └── scripts/       # Deployment scripts
└── .github/workflows/ # CI/CD pipelines
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker (for local Tectonic compilation)
- Supabase account
- Fly.io account
- Upstash account

### Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables (see `.env.example` files in each app)
4. Run database migrations
5. Start development servers: `npm run dev`

## Development

- `npm run dev` - Start all apps in development mode
- `npm run build` - Build all apps
- `npm run lint` - Lint all apps
- `npm run test` - Run tests

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions.


