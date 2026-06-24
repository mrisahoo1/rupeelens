# RupeeLens MVP Design

RupeeLens is a dark-first fintech OS for Indian spend awareness. The MVP is a Vercel-ready monorepo with a React/Vite frontend and a FastAPI backend sharing a Postgres-compatible SQLAlchemy schema with SQLite fallback.

## Architecture

The backend owns authentication, data isolation, parsing, categorization, duplicate detection, exclusions, budgets, insights, and exports. Users are separated by `user_id`; demo credentials seed and read only sample records, while the main account starts empty and is configured from environment variables. JWT sessions protect every user-owned endpoint.

The parser layer normalizes CSV, XLSX, PDF text tables, bank/UPI/card exports, and manual templates into a single transaction shape. Categorization is deterministic first: user rules, global seed rules, heuristics, optional AI flag, then Uncategorized. Credit card payments, self transfers, and UPI transfers are excluded from spend totals.

The frontend is a premium dashboard shell with glass panels, animated metrics, chart views, upload preview/confirm flow, editable transaction table, budgets, revisit board, reports, accounts, rules, settings, and a future-ready integrations page. It uses TanStack Query for API state and stores the JWT in local storage for MVP simplicity.

## Security

No plaintext main credentials are hardcoded. The main username/password or password hash comes from env. The default demo account is configurable through env and isolated through normal user ownership. Password verification supports bcrypt hashes and hashes seeded plaintext values before storage. Uploaded files are written to a per-user local dev directory; production storage is abstracted by `FILE_STORAGE_MODE`.

## Scope

Implemented now: auth, demo seed, parser preview/confirm, transaction edits, merchant rule learning, dashboard totals/charts, deterministic insights, budgets, reports CSV/PDF endpoints, docs, tests, and Vercel config. Stubbed/future: BBPS/SETU, Account Aggregator, email auto-import, and optional AI insights.
