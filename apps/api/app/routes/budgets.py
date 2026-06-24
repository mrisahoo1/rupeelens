from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Budget, User
from ..schemas import BudgetIn
router = APIRouter(prefix='/budgets', tags=['budgets'])
@router.get('')
def list_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return db.query(Budget).filter(Budget.user_id == user.id).all()
@router.post('')
def create_budget(payload: BudgetIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = Budget(user_id=user.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
@router.patch('/{budget_id}')
def update_budget(budget_id: int, payload: BudgetIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first();
    if not item: raise HTTPException(404, 'Not found')
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    db.commit(); return item
