from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Account, User
from ..schemas import AccountIn
router = APIRouter(prefix='/accounts', tags=['accounts'])
@router.get('')
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return db.query(Account).filter(Account.user_id == user.id).all()
@router.post('')
def create_account(payload: AccountIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = Account(user_id=user.id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
@router.patch('/{account_id}')
def update_account(account_id: int, payload: AccountIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first();
    if not item: raise HTTPException(404, 'Not found')
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    db.commit(); return item
@router.delete('/{account_id}')
def delete_account(account_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first();
    if not item: raise HTTPException(404, 'Not found')
    db.delete(item); db.commit(); return {'ok': True}
