# RupeeLens

RupeeLens is a personal finance intelligence dashboard for Indian users. It normalizes credit card, UPI, bank, and manual spends; excludes transfers and card payments from real spend; learns merchant rules from corrections; and presents spend awareness in a premium fintech UI.

## Local Setup

```powershell
cp .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/api/requirements.txt
npm install
python apps/api/scripts/seed_demo.py
uvicorn app.main:app --app-dir apps/api --reload --port 8000
npm run dev -w apps/web
```

Set `VITE_API_URL=http://localhost:8000/api` for local frontend development if you run the API separately. For cross-origin local dev keep `JWT_COOKIE_SECURE=false` and include the Vite origin in `CORS_ORIGINS`.

## Demo Login

Default demo credentials are `demo` / `demo123`. Demo data is isolated from the main user.

## Main User

Set `MAIN_USERNAME` and either `MAIN_PASSWORD` or `MAIN_PASSWORD_HASH` in `.env`. The main account starts empty. Do not commit real credentials.

## Verification

```powershell
cd apps/api; python -m pytest
npm run typecheck -w apps/web
npm run build -w apps/web
```

## Production Deployment on Vercel

RupeeLens is prepared for a root-level Vercel monorepo deployment:

- `vercel.json` builds `apps/web` and serves `apps/web/dist`.
- `/api/*` rewrites to the FastAPI function at `apps/api/api/index.py`.
- `/(.*)` rewrites to `index.html` for React Router SPA routes.
- Browser auth uses an HttpOnly JWT cookie; the token response remains for API compatibility.

Required production env vars:

```text
APP_ENV=production
MAIN_USERNAME=<your username>
MAIN_PASSWORD=<first boot password> OR MAIN_PASSWORD_HASH=<bcrypt hash>
JWT_SECRET=<32+ random characters>
JWT_COOKIE_SECURE=true
DATABASE_URL=<Postgres URL>
CORS_ORIGINS=https://<your-vercel-domain>,https://<custom-domain-if-any>
VITE_API_URL=/api
FILE_STORAGE_MODE=local
ENABLE_AI_INSIGHTS=false
ENABLE_OLLAMA_INSIGHTS=false
```

Production refuses insecure defaults: short/dev JWT secrets, SQLite `DATABASE_URL`, placeholder main password, missing main credentials, or insecure cookies.

See `docs/deployment.md` for the full Vercel checklist.

## Known Limitations

BBPS/SETU, Account Aggregator, email statement auto-import, and live payments are future-ready stubs only. Ollama is local/private only and should not be expected to run inside Vercel Functions. PDF parsing uses a robust text fallback but issuer-specific table extraction should be expanded with real statement samples.
