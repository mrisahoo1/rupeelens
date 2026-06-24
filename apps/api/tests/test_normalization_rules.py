from datetime import date
from app.services.normalization import clean_merchant, classify_flags, dedupe_hash

def test_clean_merchant_removes_upi_noise():
    assert clean_merchant('UPI/ZOMATO/9876543210/user@upi') == 'Zomato'
    assert clean_merchant('AMZN Mktp') == 'Amazon'

def test_credit_card_payment_and_transfer_are_excluded():
    cc = classify_flags('CRED CC PAYMENT', 'debit', 48000)
    transfer = classify_flags('SELF TRANSFER TO SBI', 'debit', 10000)
    assert cc['is_credit_card_payment'] and cc['is_excluded_from_spend']
    assert transfer['is_transfer'] and transfer['is_excluded_from_spend']

def test_refund_is_detected_for_credit_direction():
    flags = classify_flags('AMAZON REFUND', 'credit', 799)
    assert flags['is_refund']

def test_dedupe_hash_is_stable():
    a = dedupe_hash(1, date(2026,6,1), 100.0, 'Zomato', 'abc')
    b = dedupe_hash(1, date(2026,6,1), 100, 'zomato', 'abc')
    assert a == b
