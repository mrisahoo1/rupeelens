from app.config import Settings
from app.database import normalize_database_url


def test_login_sets_http_only_session_cookie_and_me_accepts_cookie(client):
    res = client.post('/api/auth/login', json={'username': 'demo', 'password': 'demo123'})
    assert res.status_code == 200
    set_cookie = res.headers.get('set-cookie', '')
    assert 'rupeelens_session=' in set_cookie
    assert 'HttpOnly' in set_cookie

    me = client.get('/api/auth/me')
    assert me.status_code == 200
    assert me.json()['username'] == 'demo'


def test_logout_clears_session_cookie(client):
    client.post('/api/auth/login', json={'username': 'demo', 'password': 'demo123'})
    res = client.post('/api/auth/logout')
    assert res.status_code == 200
    assert 'rupeelens_session=' in res.headers.get('set-cookie', '')


def test_postgres_database_urls_are_normalized_for_psycopg():
    assert normalize_database_url('postgres://u:p@host/db') == 'postgresql+psycopg://u:p@host/db'
    assert normalize_database_url('postgresql://u:p@host/db') == 'postgresql+psycopg://u:p@host/db'
    assert normalize_database_url('postgresql+psycopg://u:p@host/db') == 'postgresql+psycopg://u:p@host/db'


def test_production_settings_reject_sqlite_and_insecure_cookie():
    settings = Settings(
        app_env='production',
        jwt_secret='x' * 40,
        main_password='strong-production-password',
        database_url='sqlite:///./rupeelens.db',
        cors_origins='https://example.com',
        jwt_cookie_secure=True,
    )
    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert 'DATABASE_URL' in str(exc)
    else:
        raise AssertionError('production sqlite database should be rejected')

    settings = Settings(
        app_env='production',
        jwt_secret='x' * 40,
        main_password='strong-production-password',
        database_url='postgresql://u:p@host/db',
        cors_origins='https://example.com',
        jwt_cookie_secure=False,
    )
    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert 'JWT_COOKIE_SECURE' in str(exc)
    else:
        raise AssertionError('production insecure cookie should be rejected')
