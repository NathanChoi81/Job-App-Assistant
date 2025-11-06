# Deployment Guide

This guide covers deploying the Smart Resume & Cover Letter Generator to production.

## Prerequisites

- Supabase account (free tier)
- Fly.io account (free tier)
- Vercel account (free tier)
- Upstash account (free tier)
- OpenAI API key
- GitHub account

## Step 1: Supabase Setup

1. Create a new Supabase project
2. Run the SQL migration from `infra/supabase/schema.sql`
3. Create a storage bucket named `resumes` with public access
4. Note your project URL and anon key

## Step 2: Upstash Redis Setup

1. Create a new Redis database on Upstash
2. Note the Redis URL

## Step 3: Fly.io API Deployment

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create app: `fly apps create get-a-job-api`
4. Set secrets:
   ```bash
   fly secrets set SUPABASE_URL=...
   fly secrets set SUPABASE_KEY=...
   fly secrets set SUPABASE_JWT_SECRET=...
   fly secrets set OPENAI_API_KEY=...
   fly secrets set REDIS_URL=...
   fly secrets set CELERY_BROKER_URL=...
   fly secrets set SENTRY_DSN=...  # Optional
   fly secrets set ENVIRONMENT=production
   ```
5. Deploy: `fly deploy --config apps/api/fly.toml`

## Step 4: Fly.io Worker Deployment

1. Create app: `fly apps create get-a-job-worker`
2. Set secrets (same as API, plus):
   ```bash
   fly secrets set DOCKER_HOST=unix:///var/run/docker.sock
   ```
3. Deploy: `fly deploy --config apps/worker/fly.toml`

## Step 5: Vercel Frontend Deployment

1. Connect your GitHub repository to Vercel
2. Set root directory to `apps/frontend`
3. Set environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL` (your Fly.io API URL)
4. Deploy

## Step 6: GitHub Actions Setup

1. Add secrets to GitHub repository:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `FLY_API_TOKEN`
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - All API secrets (same as Fly.io)

## Step 7: Umami Analytics (Optional)

1. Deploy Umami to Vercel using their guide
2. Connect to your Supabase database
3. Add Umami script to frontend `layout.tsx`

## Monitoring

- Check Fly.io logs: `fly logs -a get-a-job-api`
- Monitor usage in Fly.io dashboard
- Check Supabase dashboard for database usage
- Monitor Upstash for Redis usage

## Free Tier Limits

- **Fly.io**: ~2 VM hours/day (auto-scales to 0)
- **Supabase**: 500 MB DB, 1 GB storage
- **Upstash**: 10 MB data, 10K req/day
- **Vercel**: 100 GB bandwidth/month
- **OpenAI**: Pay-as-you-go (~$0.001 per JD)

