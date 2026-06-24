# Security

- Main credentials are read from env only.
- Passwords are stored as bcrypt hashes.
- JWT protects user-owned APIs.
- Demo user data is isolated by `user_id` and marked with `account_type=demo`.
- Upload directories are partitioned by user ID in local dev.
- Production should use Postgres and blob storage with private object access.
- Optional AI integrations are disabled unless `ENABLE_AI_INSIGHTS=true` and an API key is provided.
