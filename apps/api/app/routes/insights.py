from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..services.analytics import build_insights
router = APIRouter(prefix='/insights', tags=['insights'])
@router.get('')
def insights(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return build_insights(db, user.id, month)
@router.post('/regenerate')
def regenerate(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return {'insights': build_insights(db, user.id, month)}
