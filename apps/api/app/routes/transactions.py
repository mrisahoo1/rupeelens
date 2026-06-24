from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Transaction, User
from ..schemas import TransactionPatch, ManualTransaction, BulkUpdate
from ..services.normalization import classify_flags, dedupe_hash
from ..services.rules import categorize, learn_user_rule
router = APIRouter(prefix='/transactions', tags=['transactions'])
@router.get('')
def list_transactions(month: str | None = None, category: str | None = None, merchant: str | None = None, payment_mode: str | None = None, revisit: bool | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if month: q = q.filter(Transaction.transaction_date >= f'{month}-01', Transaction.transaction_date < f'{month}-32')
    if category: q = q.filter(Transaction.category == category)
    if merchant: q = q.filter(Transaction.merchant_normalized.ilike(f'%{merchant}%'))
    if payment_mode: q = q.filter(Transaction.payment_mode == payment_mode)
    if revisit is not None: q = q.filter(Transaction.revisit_flag == revisit)
    return q.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).limit(500).all()
@router.patch('/{tx_id}')
def patch_transaction(tx_id: int, payload: TransactionPatch, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx: raise HTTPException(404, 'Not found')
    old_category = tx.category
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(tx,k,v)
    db.commit(); db.refresh(tx)
    if payload.category and payload.category != old_category:
        learn_user_rule(db, user.id, tx.merchant_normalized, payload.category, payload.subcategory)
    return tx
@router.post('/manual')
def manual(payload: ManualTransaction, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = categorize(db, user.id, payload.description_raw); flags = classify_flags(payload.description_raw, payload.direction, payload.amount)
    if payload.category: cat['category'] = payload.category; cat['category_source'] = 'manual'
    tx = Transaction(user_id=user.id, source_type='manual', source_file_name='manual', transaction_date=payload.transaction_date, description_raw=payload.description_raw, merchant_raw=payload.description_raw, amount=payload.amount, direction=payload.direction, payment_mode=payload.payment_mode, dedupe_hash=dedupe_hash(user.id, payload.transaction_date, payload.amount, cat['merchant_normalized'], None), remark=payload.remark, revisit_flag=payload.revisit_flag, **cat, **flags)
    db.add(tx); db.commit(); db.refresh(tx); return tx
@router.post('/bulk-update')
def bulk(payload: BulkUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    txs = db.query(Transaction).filter(Transaction.user_id == user.id, Transaction.id.in_(payload.ids)).all()
    for tx in txs:
        if payload.category: tx.category = payload.category; learn_user_rule(db, user.id, tx.merchant_normalized, payload.category)
        if payload.tags is not None: tx.tags = payload.tags
        if payload.revisit_flag is not None: tx.revisit_flag = payload.revisit_flag
    db.commit(); return {'updated': len(txs)}
