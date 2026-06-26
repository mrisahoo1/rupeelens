from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / '.env', extra='ignore')
    app_env: str = 'development'
    main_username: str = 'mrisahoo'
    main_password: str | None = None
    main_password_hash: str | None = None
    demo_username: str = 'demo'
    demo_password: str = 'demo123'
    demo_password_hash: str | None = None
    jwt_secret: str = 'dev-only-change-me'
    jwt_algorithm: str = 'HS256'
    jwt_cookie_name: str = 'rupeelens_session'
    jwt_cookie_secure: bool = False
    jwt_cookie_samesite: str = 'lax'
    jwt_cookie_domain: str | None = None
    database_url: str = 'sqlite:///./rupeelens.db'
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    enable_ai_insights: bool = False
    openai_api_key: str | None = None
    file_storage_mode: str = 'local'
    upload_dir: str = 'uploads'
    enable_ollama_insights: bool = False
    ollama_url: str = 'http://127.0.0.1:11434'
    ollama_model: str = 'llama3.2'
    ollama_timeout_seconds: int = 20

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {'production', 'prod'}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]

    def validate_runtime(self) -> None:
        if self.is_production:
            if not self.jwt_secret or self.jwt_secret == 'dev-only-change-me' or len(self.jwt_secret) < 32:
                raise RuntimeError('JWT_SECRET must be set to a 32+ character random value in production')
            if self.database_url.startswith('sqlite'):
                raise RuntimeError('DATABASE_URL must point to Postgres-compatible storage in production')
            if self.main_password and self.main_password == 'replace_with_new_secure_password':
                raise RuntimeError('MAIN_PASSWORD must be changed before production deployment')
            if not self.main_password and not self.main_password_hash:
                raise RuntimeError('MAIN_PASSWORD or MAIN_PASSWORD_HASH is required in production')
            if not self.jwt_cookie_secure:
                raise RuntimeError('JWT_COOKIE_SECURE must be true in production')
            if not self.cors_origin_list:
                raise RuntimeError('CORS_ORIGINS must include the deployed web origin in production')

@lru_cache
def get_settings() -> Settings:
    return Settings()
