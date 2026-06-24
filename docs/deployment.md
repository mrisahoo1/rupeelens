# Deployment

1. Create a Vercel project from this repo.
2. Add env vars from `.env.example`.
3. Use Postgres for `DATABASE_URL` in production, for example Neon, Supabase, or Vercel Postgres.
4. Keep `JWT_SECRET` long and random.
5. Set either `MAIN_PASSWORD` for first boot or `MAIN_PASSWORD_HASH` for an already-hashed bcrypt password.
6. Deploy preview with `vercel deploy . -y`; promote to production only when ready.

Uploaded file storage is local for dev. For production, keep `FILE_STORAGE_MODE` ready for blob-backed storage; the storage boundary is isolated in the upload route.
