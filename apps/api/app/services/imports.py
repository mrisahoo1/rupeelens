from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Transaction
from ..parsers.base import ParsedTransaction
from .normalization import classify_flags, dedupe_hash, parse_date
from .rules import categorize
from .confidence import score_transaction_confidence

def _json_safe_row(row: dict) -> dict:
    safe = row.copy()
    for key in ('transaction_date', 'posting_date'):
        if isinstance(safe.get(key), date):
            safe[key] = safe[key].isoformat()
    return safe

def preview_rows(db: Session, user_id: int, parsed: list[ParsedTransaction], source_type: str, source_file_name: str, account=None) -> list[dict]:
    rows = []
    for item in parsed:
        cat = categorize(db, user_id, item.description_raw)
        flags = classify_flags(item.description_raw, item.direction, item.amount)
        row_hash = dedupe_hash(user_id, item.transaction_date, item.amount, cat['merchant_normalized'], item.reference_id)
        duplicate = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.dedupe_hash == row_hash).first() is not None
        confidence = score_transaction_confidence(item.description_raw, cat['merchant_normalized'], item.amount, item.transaction_date, item.direction, cat['category'], cat['category_source'], item.payment_mode, item.reference_id, duplicate, flags['is_excluded_from_spend'])
        row = {**item.__dict__, **cat, **flags, 'source_type': source_type, 'source_file_name': source_file_name, 'dedupe_hash': row_hash, 'is_duplicate': duplicate, 'confidence_score': confidence.score, 'confidence_reasons': confidence.reasons, 'account_id': getattr(account, 'id', None), 'card_name': getattr(account, 'name', None) if getattr(account, 'type', '') == 'credit_card' else None, 'card_last4': getattr(account, 'last4', None)}
        rows.append(_json_safe_row(row))
    return rows

def confirm_rows(db: Session, user_id: int, batch_id: int, rows: list[dict]) -> int:
    inserted = 0
    for row in rows:
        data = row.copy()
        data['user_id'] = user_id
        data['import_batch_id'] = batch_id
        data.pop('merchant_raw', None)
        if isinstance(data.get('transaction_date'), str):
            data['transaction_date'] = parse_date(data['transaction_date'])
        if isinstance(data.get('posting_date'), str):
            data['posting_date'] = parse_date(data['posting_date'])
        tx = Transaction(**{k: v for k, v in data.items() if hasattr(Transaction, k)})
        db.add(tx)
        try:
            db.commit(); inserted += 1
        except IntegrityError:
            db.rollback()
    return inserted

