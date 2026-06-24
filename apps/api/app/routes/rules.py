from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import MerchantRule, User
from ..schemas import RuleIn
router = APIRouter(prefix='/rules', tags=['rules'])
@router.get('')
def list_rules(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return db.query(MerchantRule).filter((MerchantRule.user_id == user.id) | (MerchantRule.is_global == True)).order_by(MerchantRule.is_global.desc(), MerchantRule.priority.asc()).all()
@router.post('')
def create_rule(payload: RuleIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = MerchantRule(user_id=user.id, is_global=False, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
@router.patch('/{rule_id}')
def update_rule(rule_id: int, payload: RuleIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(MerchantRule).filter(MerchantRule.id == rule_id, MerchantRule.user_id == user.id).first();
    if not item: raise HTTPException(404, 'Not found')
    for k,v in payload.model_dump().items(): setattr(item,k,v)
    db.commit(); return item
@router.delete('/{rule_id}')
def delete_rule(rule_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(MerchantRule).filter(MerchantRule.id == rule_id, MerchantRule.user_id == user.id).first();
    if not item: raise HTTPException(404, 'Not found')
    db.delete(item); db.commit(); return {'ok': True}
