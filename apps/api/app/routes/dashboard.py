from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..services.analytics import summary
router = APIRouter(prefix='/dashboard', tags=['dashboard'])
@router.get('/summary')
def dashboard_summary(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)): return summary(db, user.id, month)
@router.get('/charts')
def dashboard_charts(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = summary(db, user.id, month)
    return {'category': [{'name': k, 'value': v} for k,v in data['category'].items()], 'daily': [{'date': k, 'amount': v} for k,v in data['daily'].items()], 'merchant': [{'name': k, 'value': v} for k,v in data['merchant'].items()], 'mode': [{'name': k, 'value': v} for k,v in data['mode'].items()], 'card': [{'name': k, 'value': v} for k,v in data['card'].items()]}
