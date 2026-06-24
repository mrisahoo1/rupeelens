from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    main_username: str = 'mrisahoo'
    main_password: str | None = None
    main_password_hash: str | None = None
    demo_username: str = 'demo'
    demo_password: str = 'demo123'
    demo_password_hash: str | None = None
    jwt_secret: str = 'dev-only-change-me'
    jwt_algorithm: str = 'HS256'
    database_url: str = 'sqlite:///./rupeelens.db'
    enable_ai_insights: bool = False
    openai_api_key: str | None = None
    file_storage_mode: str = 'local'
    upload_dir: str = 'uploads'

@lru_cache
def get_settings() -> Settings:
    return Settings()
