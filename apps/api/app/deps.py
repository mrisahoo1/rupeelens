from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)

def _token_from_request(request: Request, creds: HTTPAuthorizationCredentials | None) -> str | None:
    if creds and creds.credentials:
        return creds.credentials
    return request.cookies.get(get_settings().jwt_cookie_name)

def get_current_user(request: Request, creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    token = _token_from_request(request, creds)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing token')
    try:
        payload = decode_token(token)
        user = db.get(User, int(payload['sub']))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token') from exc
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    return user
