# RupeeLens MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-shaped RupeeLens MVP with isolated auth, upload parsing, normalized transactions, premium frontend, docs, tests, and Vercel readiness.

**Architecture:** FastAPI owns secure data and deterministic finance logic; React/Vite renders a premium fintech dashboard and editing workflows. SQLite is local fallback while the SQLAlchemy schema remains Postgres-compatible.

**Tech Stack:** React, Vite, TypeScript, Tailwind, Recharts, Framer Motion, TanStack Query, FastAPI, SQLAlchemy, Pandas, pdfplumber, bcrypt, PyJWT, pytest.

---

### Task 1: Backend Foundation
- [x] Create config, database, models, schemas, security, seed data, and app bootstrap.
- [x] Add JWT auth, bcrypt password verification, role/account type fields, and demo/main user isolation.
- [x] Add tests for auth and demo isolation.

### Task 2: Parser And Rules Engine
- [x] Create BaseParser, CSV/XLSX/PDF/fallback parsers, merchant normalization, deterministic categories, duplicate hashes, refund/exclusion detection.
- [x] Add tests for normalization, categorization, duplicate detection, exclusions, and refunds.

### Task 3: API Surface
- [x] Add uploads, transactions, dashboard, insights, budgets, rules, accounts, reports, and integration stubs.
- [x] Add transaction edit rule-learning behavior.

### Task 4: Frontend MVP
- [x] Create premium login, shell navigation, dashboard, upload center, transactions, insights, budgets, revisit, reports, accounts, rules, settings, and integrations screens.
- [x] Add API client, protected routes, demo banner, and responsive visual system.

### Task 5: Docs And Verification
- [x] Add README, deployment, parser, security, and architecture docs.
- [ ] Install dependencies.
- [ ] Run pytest, frontend typecheck, and frontend build.
- [ ] Fix verification failures.
