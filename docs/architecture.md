# Architecture

RupeeLens is a Vercel-ready monorepo. `apps/web` contains the React/Vite client. `apps/api` contains the FastAPI app and Vercel-compatible `api/index.py` entrypoint.

The backend is intentionally deterministic for finance correctness: parsers normalize rows, the rules engine categorizes merchants, exclusions are marked before aggregation, and dashboard totals only include user-owned transactions. Demo and main data never mix because every table with user content includes `user_id` and route queries always filter by the authenticated user.
