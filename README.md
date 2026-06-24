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

Set `VITE_API_URL=http://localhost:8000/api` for local frontend development if you run the API separately.

## Demo Login

Default demo credentials are `demo` / `demo123`. Demo data is isolated from the main user.

## Main User

Set `MAIN_USERNAME` and either `MAIN_PASSWORD` or `MAIN_PASSWORD_HASH` in `.env`. The main account starts empty.

## Verification

```powershell
cd apps/api; pytest
npm run typecheck -w apps/web
npm run build -w apps/web
```

## Vercel

Use Vercel project env vars from `.env.example`. For production, use Postgres (`DATABASE_URL`) and a blob storage implementation behind `FILE_STORAGE_MODE`.

```powershell
vercel deploy . -y
```

## Known Limitations

BBPS/SETU, Account Aggregator, email statement auto-import, and AI insights are stubbed or feature-flagged for later. PDF parsing uses a robust text fallback but issuer-specific table extraction should be expanded with real statement samples.
