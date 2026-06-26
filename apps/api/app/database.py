from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings

class Base(DeclarativeBase):
    pass

def normalize_database_url(url: str) -> str:
    if url.startswith('postgres://'):
        return 'postgresql+psycopg://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url

def make_engine(url: str | None = None):
    db_url = normalize_database_url(url or get_settings().database_url)
    connect_args = {'check_same_thread': False} if db_url.startswith('sqlite') else {}
    return create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
