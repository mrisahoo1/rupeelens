# Deployment

RupeeLens is configured as a Vercel monorepo deployment:

- Frontend: `apps/web` Vite build, output at `apps/web/dist`.
- Backend: FastAPI serverless function at `apps/api/api/index.py`.
- Routing: `/api/*` rewrites to FastAPI, all other paths rewrite to `index.html` for React Router SPA support.

## Vercel Project Settings

Use the repository root as the Vercel root directory.

Recommended settings:

```text
Install Command: npm ci && python -m pip install -r apps/api/requirements.txt
Build Command: npm run build -w apps/web
Output Directory: apps/web/dist
```

These are also encoded in `vercel.json`.

## Required Production Environment Variables

Set these in Vercel Project Settings, not in code:

```text
APP_ENV=production
MAIN_USERNAME=<your username>
MAIN_PASSWORD=<temporary first-boot password> OR MAIN_PASSWORD_HASH=<bcrypt hash>
DEMO_USERNAME=demo
DEMO_PASSWORD=<change if desired>
JWT_SECRET=<32+ random characters>
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=lax
DATABASE_URL=<postgresql/postgres URL from Neon/Supabase/Vercel Postgres>
CORS_ORIGINS=https://<your-vercel-domain>,https://<your-custom-domain>
VITE_API_URL=/api
FILE_STORAGE_MODE=local
ENABLE_AI_INSIGHTS=false
ENABLE_OLLAMA_INSIGHTS=false
```

`DATABASE_URL` must be Postgres-compatible in production. SQLite is allowed only for local development. The app accepts `postgres://`, `postgresql://`, and `postgresql+psycopg://` URLs and normalizes them for SQLAlchemy.

## Auth and Cookies

The API returns the JWT for compatibility, but the browser session is secured with an HttpOnly cookie named by `JWT_COOKIE_NAME`. In production set `JWT_COOKIE_SECURE=true`. The web client sends `credentials: include` on API calls.

## CORS

Do not use wildcard CORS in production. Set `CORS_ORIGINS` to the deployed frontend origins, comma-separated. Same-origin Vercel deployments can keep `VITE_API_URL=/api`.

## Storage

Local upload storage is for development and preview only. For production financial statements, connect `FILE_STORAGE_MODE` to private blob storage before using real statements at scale.

## Commands

```powershell
npm ci
npm run typecheck -w apps/web
npm run build -w apps/web
cd apps/api; python -m pytest
```

Deploy preview:

```powershell
vercel deploy .
```

Promote to production only after preview verification:

```powershell
vercel deploy --prod .
```
