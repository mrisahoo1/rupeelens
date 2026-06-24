from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Transaction
from ..parsers.base import ParsedTransaction
from .normalization import classify_flags, dedupe_hash
from .rules import categorize

def preview_rows(db: Session, user_id: int, parsed: list[ParsedTransaction], source_type: str, source_file_name: str, account=None) -> list[dict]:
    rows = []
    for item in parsed:
        cat = categorize(db, user_id, item.description_raw)
        flags = classify_flags(item.description_raw, item.direction, item.amount)
        row_hash = dedupe_hash(user_id, item.transaction_date, item.amount, cat['merchant_normalized'], item.reference_id)
        duplicate = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.dedupe_hash == row_hash).first() is not None
        rows.append({**item.__dict__, **cat, **flags, 'source_type': source_type, 'source_file_name': source_file_name, 'dedupe_hash': row_hash, 'is_duplicate': duplicate, 'account_id': getattr(account, 'id', None), 'card_name': getattr(account, 'name', None) if getattr(account, 'type', '') == 'credit_card' else None, 'card_last4': getattr(account, 'last4', None)})
    return rows

def confirm_rows(db: Session, user_id: int, batch_id: int, rows: list[dict]) -> int:
    inserted = 0
    for row in rows:
        data = row.copy()
        data['user_id'] = user_id
        data['import_batch_id'] = batch_id
        data.pop('merchant_raw', None)
        tx = Transaction(**{k: v for k, v in data.items() if hasattr(Transaction, k)})
        db.add(tx)
        try:
            db.commit(); inserted += 1
        except IntegrityError:
            db.rollback()
    return inserted
