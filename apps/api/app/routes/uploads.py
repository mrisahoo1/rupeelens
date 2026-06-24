import os, shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Account, ImportBatch, User
from ..parsers import parser_for
from ..services.imports import preview_rows, confirm_rows
router = APIRouter(prefix='/uploads', tags=['uploads'])
@router.post('')
def upload(source_type: str = Form(...), account_id: int | None = Form(None), files: list[UploadFile] = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.account_type == 'demo': raise HTTPException(403, 'Demo uploads are disabled')
    settings = get_settings(); batches = []
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first() if account_id else None
    user_dir = os.path.join(settings.upload_dir, str(user.id)); os.makedirs(user_dir, exist_ok=True)
    for file in files:
        path = os.path.join(user_dir, file.filename)
        with open(path, 'wb') as out: shutil.copyfileobj(file.file, out)
        try:
            parsed = parser_for(file.filename).parse(path, source_type)
            rows = preview_rows(db, user.id, parsed, source_type, file.filename, account)
            batch = ImportBatch(user_id=user.id, account_id=account_id, source_type=source_type, source_file_name=file.filename, parsed_rows=rows, errors=[])
        except Exception as exc:
            batch = ImportBatch(user_id=user.id, account_id=account_id, source_type=source_type, source_file_name=file.filename, parsed_rows=[], errors=[str(exc)])
        db.add(batch); db.commit(); db.refresh(batch); batches.append(batch)
    return batches
@router.get('')
def list_uploads(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return db.query(ImportBatch).filter(ImportBatch.user_id == user.id).order_by(ImportBatch.id.desc()).all()
@router.get('/{batch_id}')
def get_upload(batch_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id, ImportBatch.user_id == user.id).first();
    if not batch: raise HTTPException(404, 'Not found')
    return batch
@router.post('/{batch_id}/confirm')
def confirm(batch_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id, ImportBatch.user_id == user.id).first();
    if not batch: raise HTTPException(404, 'Not found')
    inserted = confirm_rows(db, user.id, batch.id, batch.parsed_rows); batch.status='imported'; db.commit(); return {'inserted': inserted, 'batch_id': batch.id}
@router.delete('/{batch_id}')
def delete(batch_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id, ImportBatch.user_id == user.id).first();
    if not batch: raise HTTPException(404, 'Not found')
    db.delete(batch); db.commit(); return {'ok': True}
