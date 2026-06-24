from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from ..models import MerchantRule
from .categories import GLOBAL_RULES
from .normalization import clean_merchant

def seed_global_rules(db: Session):
    if db.query(MerchantRule).filter(MerchantRule.is_global == True).first():
        return
    for i, (pattern, merchant, category) in enumerate(GLOBAL_RULES):
        db.add(MerchantRule(pattern=pattern, merchant_normalized=merchant, category=category, priority=i, is_global=True, confidence=0.95))
    db.commit()

def categorize(db: Session, user_id: int, description: str) -> dict:
    merchant = clean_merchant(description)
    low = f'{description} {merchant}'.lower()
    rules = db.query(MerchantRule).filter(or_(MerchantRule.user_id == user_id, MerchantRule.is_global == True)).order_by(MerchantRule.user_id.desc().nullslast(), MerchantRule.priority.asc()).all()
    for rule in rules:
        if rule.pattern.lower() in low or fuzz.partial_ratio(rule.pattern.lower(), low) > 90:
            rule.last_used_at = datetime.utcnow()
            return {'merchant_normalized': rule.merchant_normalized, 'category': rule.category, 'subcategory': rule.subcategory, 'category_source': 'rule' if rule.user_id else 'global_rule', 'confidence_score': rule.confidence}
    heuristics = [('rent','Rent & Housing'),('grocery','Groceries'),('restaurant','Food & Dining'),('movie','Entertainment'),('insurance','Insurance'),('mutual fund','Investments'),('atm','Cash Withdrawal'),('fee','Fees & Charges')]
    for key, category in heuristics:
        if key in low:
            return {'merchant_normalized': merchant, 'category': category, 'subcategory': None, 'category_source': 'fallback', 'confidence_score': 0.65}
    return {'merchant_normalized': merchant, 'category': 'Uncategorized', 'subcategory': None, 'category_source': 'fallback', 'confidence_score': 0.35}

def learn_user_rule(db: Session, user_id: int, merchant: str, category: str, subcategory: str | None = None):
    existing = db.query(MerchantRule).filter(MerchantRule.user_id == user_id, MerchantRule.pattern == merchant.lower()).first()
    if existing:
        existing.category = category
        existing.subcategory = subcategory
        existing.created_from_user_correction = True
    else:
        db.add(MerchantRule(user_id=user_id, pattern=merchant.lower(), merchant_normalized=merchant, category=category, subcategory=subcategory, priority=1, is_global=False, created_from_user_correction=True, confidence=0.99))
    db.commit()
