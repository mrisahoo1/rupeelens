from datetime import date
from app.services.confidence import score_transaction_confidence


def test_confidence_score_rewards_known_rule_and_reference():
    result = score_transaction_confidence(
        description='UPI/ZOMATO/ORDER 123',
        merchant='Zomato',
        amount=321,
        transaction_date=date(2026, 6, 25),
        direction='debit',
        category='Food & Dining',
        category_source='global_rule',
        payment_mode='upi',
        reference_id='UTR123',
        is_duplicate=False,
        is_excluded=False,
    )
    assert result.score >= 0.85
    assert 'Known merchant/category rule' in result.reasons


def test_confidence_score_penalizes_unknown_fallback_without_reference():
    result = score_transaction_confidence(
        description='random transfer text 999999',
        merchant='Unknown Merchant',
        amount=0,
        transaction_date=None,
        direction='debit',
        category='Uncategorized',
        category_source='fallback',
        payment_mode='manual',
        reference_id=None,
        is_duplicate=True,
        is_excluded=False,
    )
    assert result.score <= 0.35
    assert 'Needs merchant review' in result.reasons
