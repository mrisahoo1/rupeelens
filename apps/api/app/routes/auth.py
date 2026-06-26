from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import LoginRequest, TokenResponse
from ..security import verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=['auth'])

def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.jwt_cookie_name,
        value=token,
        max_age=60 * 60 * 12,
        httponly=True,
        secure=settings.jwt_cookie_secure,
        samesite=settings.jwt_cookie_samesite,
        domain=settings.jwt_cookie_domain,
        path='/',
    )

@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token(user.id, user.username, user.role, user.account_type)
    _set_session_cookie(response, token)
    return {'access_token': token, 'user': {'id': user.id, 'username': user.username, 'role': user.role, 'account_type': user.account_type}}

@router.post('/logout')
def logout(response: Response):
    settings = get_settings()
    response.delete_cookie(key=settings.jwt_cookie_name, domain=settings.jwt_cookie_domain, path='/')
    return {'ok': True}

@router.get('/me')
def me(user: User = Depends(get_current_user)):
    return {'id': user.id, 'username': user.username, 'role': user.role, 'account_type': user.account_type}
