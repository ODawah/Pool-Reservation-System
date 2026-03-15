# Deploy on Vercel (FastAPI + Frontend)

This repo is now configured so:
- Backend API is served by Vercel at `/api/*`
- Frontend static files are served by Vercel from your project files

## 1) Required environment variables

Set these in Vercel Project Settings -> Environment Variables:

- `DATABASE_URL` (required for production)
  - Recommended: Vercel Postgres or Neon/Supabase Postgres URL
  - Example format: `postgresql://USER:PASSWORD@HOST:5432/DBNAME`

If `DATABASE_URL` is not set, the app falls back to local SQLite (`thebreakroom.db`), which is not persistent on Vercel.

## 2) Frontend placement

Choose one:

- Plain static frontend:
  - Put files in `public/` (for example `public/index.html`)
- Built frontend (React/Vite/Next/etc):
  - Deploy as a separate Vercel project, or add your framework config in this repo

For API calls from frontend, use relative paths like:
- `fetch('/api/tables/')`
- `fetch('/api/revenue/last-month/closeout', { method: 'POST' })`

## 3) Deploy

From the repo root:

```bash
vercel
```

For production:

```bash
vercel --prod
```

## 4) Useful checks after deploy

- `https://<your-project>.vercel.app/api/docs`
- `https://<your-project>.vercel.app/api/tables/`

