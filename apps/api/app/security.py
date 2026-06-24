from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from .config import get_settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except ValueError:
        return False

def create_access_token(user_id: int, username: str, role: str, account_type: str) -> str:
    settings = get_settings()
    payload = {
        'sub': str(user_id), 'username': username, 'role': role, 'account_type': account_type,
        'exp': datetime.now(timezone.utc) + timedelta(hours=12), 'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
