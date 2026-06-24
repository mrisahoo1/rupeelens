import os, tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db, make_engine
from app.config import get_settings
from app.main import app
from app.seed import ensure_users

@pytest.fixture()
def client(monkeypatch):
    fd, path = tempfile.mkstemp(suffix='.db'); os.close(fd)
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{path}')
    monkeypatch.setenv('JWT_SECRET', 'test-secret-that-is-long-enough')
    monkeypatch.setenv('MAIN_USERNAME', 'main')
    monkeypatch.setenv('MAIN_PASSWORD', 'mainpass123')
    get_settings.cache_clear()
    engine = make_engine(f'sqlite:///{path}')
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSession(); ensure_users(db); db.close()
    def override_db():
        db = TestingSession()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    try: os.remove(path)
    except OSError: pass

@pytest.fixture()
def demo_headers(client):
    res = client.post('/api/auth/login', json={'username':'demo','password':'demo123'})
    return {'Authorization': f'Bearer {res.json()["access_token"]}'}

@pytest.fixture()
def main_headers(client):
    res = client.post('/api/auth/login', json={'username':'main','password':'mainpass123'})
    return {'Authorization': f'Bearer {res.json()["access_token"]}'}

