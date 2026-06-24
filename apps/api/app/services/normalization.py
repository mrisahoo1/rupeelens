import hashlib, re
from datetime import date
from dateutil import parser as date_parser
from rapidfuzz import fuzz
from .categories import GLOBAL_RULES

NOISE = [r'UPI/', r'UPI-', r'IMPS/', r'NEFT/', r'RTGS/', r'\bTO\b', r'\bFROM\b', r'\bP2A\b', r'\bP2P\b']

def parse_date(value) -> date:
    if isinstance(value, date):
        return value
    return date_parser.parse(str(value), dayfirst=True, fuzzy=True).date()

def parse_amount(value) -> float:
    text = str(value or '0').replace(',', '').replace('₹', '').strip()
    if text in {'', 'nan', 'None'}:
        return 0.0
    neg = text.startswith('(') and text.endswith(')')
    text = text.strip('()')
    amount = float(re.sub(r'[^0-9.\-]', '', text) or 0)
    return -amount if neg else amount

def clean_merchant(raw: str) -> str:
    text = (raw or '').strip()
    for pattern in NOISE:
        text = re.sub(pattern, ' ', text, flags=re.I)
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+', ' ', text)
    text = re.sub(r'\b\d{6,}\b', ' ', text)
    text = re.sub(r'[^A-Za-z0-9 &.-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip(' -/')
    low = text.lower()
    aliases = {'amzn mktp': 'Amazon', 'swiggy payments': 'Swiggy', 'irctc upi': 'IRCTC', 'cred cc payment': 'Credit Card Payment', 'hdfc credit card payment': 'Credit Card Payment', 'self transfer': 'Transfer'}
    for key, value in aliases.items():
        if key in low:
            return value
    for pattern, merchant, _ in GLOBAL_RULES:
        if pattern in low or fuzz.partial_ratio(pattern, low) > 92:
            return merchant
    return text.title() if text else 'Unknown Merchant'

def classify_flags(description: str, direction: str, amount: float) -> dict:
    text = (description or '').lower()
    is_refund = direction == 'credit' or any(k in text for k in ['refund', 'reversal', 'cashback', 'chargeback'])
    is_cc = any(k in text for k in ['credit card payment', 'cc payment', 'cred cc', 'hdfc credit card', 'icici credit card', 'sbi card payment', 'axis card payment'])
    is_transfer = any(k in text for k in ['self transfer', 'bank transfer', 'upi transfer', 'neft', 'imps', 'rtgs', 'own account'])
    return {'is_refund': is_refund, 'is_credit_card_payment': is_cc, 'is_transfer': is_transfer, 'is_excluded_from_spend': is_cc or is_transfer}

def dedupe_hash(user_id: int, transaction_date: date, amount: float, merchant: str, reference_id: str | None) -> str:
    base = f'{user_id}|{transaction_date.isoformat()}|{abs(amount):.2f}|{merchant.lower()}|{reference_id or ""}'
    return hashlib.sha256(base.encode('utf-8')).hexdigest()

