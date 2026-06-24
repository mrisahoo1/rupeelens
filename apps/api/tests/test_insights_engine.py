from datetime import date

from sqlalchemy.orm import sessionmaker

from app.database import Base, make_engine
from app.models import Budget, Transaction, User
from app.services.analytics import build_insights


def _db(tmp_path):
    engine = make_engine(f'sqlite:///{tmp_path / "insights.db"}')
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def _tx(user_id, day, merchant, amount, category, mode='credit_card', direction='debit', **flags):
    return Transaction(
        user_id=user_id,
        source_type='test',
        source_file_name='synthetic',
        transaction_date=day,
        description_raw=flags.pop('description_raw', merchant),
        merchant_raw=merchant,
        merchant_normalized=merchant,
        amount=amount,
        direction=direction,
        category=category,
        payment_mode=mode,
        dedupe_hash=f'{user_id}-{day}-{merchant}-{amount}-{len(merchant)}-{mode}-{direction}',
        confidence_score=flags.pop('confidence_score', 0.92),
        category_source='rule',
        **flags,
    )


def _by_type(insights):
    return {item['type']: item for item in insights}


def test_monthly_insight_engine_emits_explainable_deterministic_cards(tmp_path):
    db = _db(tmp_path)
    user = User(username='insight-main', password_hash='x', role='user', account_type='main')
    db.add(user)
    db.flush()

    # Previous month baseline for category spike detection.
    db.add_all([
        _tx(user.id, date(2026, 5, 5), 'Zomato', 2000, 'Food & Dining', 'upi'),
        _tx(user.id, date(2026, 5, 8), 'Amazon', 28000, 'Shopping'),
    ])

    # Current month has every requested signal family.
    db.add_all([
        _tx(user.id, date(2026, 6, 1), 'Zomato', 2200, 'Food & Dining', 'upi'),
        _tx(user.id, date(2026, 6, 2), 'Swiggy', 1800, 'Food & Dining', 'upi'),
        _tx(user.id, date(2026, 6, 3), 'Local Cafe', 250, 'Food & Dining', 'upi'),
        _tx(user.id, date(2026, 6, 4), 'Tea Stall', 120, 'Food & Dining', 'upi'),
        _tx(user.id, date(2026, 6, 5), 'Auto UPI', 180, 'Transport', 'upi'),
        _tx(user.id, date(2026, 6, 6), 'Netflix', 649, 'Subscriptions', 'credit_card'),
        _tx(user.id, date(2026, 6, 13), 'Netflix', 649, 'Subscriptions', 'credit_card'),
        _tx(user.id, date(2026, 6, 20), 'Netflix', 649, 'Subscriptions', 'credit_card'),
        _tx(user.id, date(2026, 6, 7), 'Amazon', 9500, 'Shopping', 'credit_card'),
        _tx(user.id, date(2026, 6, 14), 'Amazon', 8700, 'Shopping', 'credit_card'),
        _tx(user.id, date(2026, 6, 21), 'Amazon', 6400, 'Shopping', 'credit_card'),
        _tx(user.id, date(2026, 6, 10), 'Amazon', 3500, 'Shopping', 'credit_card'),
        _tx(user.id, date(2026, 6, 11), 'Amazon', 2100, 'Shopping', 'credit_card'),
        _tx(user.id, date(2026, 6, 12), 'Refund Amazon', 1500, 'Shopping', 'credit_card', direction='credit', is_refund=True, description_raw='Amazon Refund Reversal'),
        _tx(user.id, date(2026, 6, 15), 'CRED', 42000, 'Credit Card Payment', 'upi', is_credit_card_payment=True, is_excluded_from_spend=True, description_raw='CRED CC PAYMENT'),
        _tx(user.id, date(2026, 6, 16), 'Self Transfer', 12000, 'Bank Transfer', 'bank', is_transfer=True, is_excluded_from_spend=True, description_raw='NEFT SELF TRANSFER TO OWN ACCOUNT'),
        _tx(user.id, date(2026, 6, 17), 'Unknown Wire', 18000, 'Uncategorized', 'bank', confidence_score=0.31, description_raw='ACH/XYZ/9911288'),
    ])
    db.add_all([
        Budget(user_id=user.id, month='2026-06', category='Overall', amount=26000),
        Budget(user_id=user.id, month='2026-06', category='Shopping', amount=12000),
    ])
    db.commit()

    insights = build_insights(db, user.id, '2026-06')
    by_type = _by_type(insights)

    expected_types = {
        'category_spike',
        'small_upi_impulse',
        'recurring_subscription',
        'weekend_spending',
        'merchant_concentration',
        'budget_risk',
        'refunds',
        'excluded_transfers',
        'unusual_transactions',
    }
    assert expected_types.issubset(by_type.keys())

    for insight in insights:
        assert insight['type']
        assert 0 <= insight['confidence'] <= 1
        assert insight['confidence_label'] in {'high', 'medium', 'low'}
        assert insight['reasons'], insight
        assert isinstance(insight['reasons'], list)
        assert insight['evidence'], insight
        assert isinstance(insight['evidence'], dict)
        assert 'title' in insight and 'body' in insight and 'severity' in insight

    assert by_type['category_spike']['evidence']['category'] == 'Food & Dining'
    assert by_type['category_spike']['evidence']['previous_amount'] == 2000
    assert by_type['small_upi_impulse']['evidence']['count'] == 3
    assert by_type['recurring_subscription']['evidence']['merchant'] == 'Netflix'
    assert by_type['weekend_spending']['evidence']['weekend_share'] >= 0.35
    assert by_type['merchant_concentration']['evidence']['merchant'] == 'Amazon'
    assert by_type['budget_risk']['evidence']['budget_amount'] == 26000
    assert by_type['refunds']['evidence']['refund_amount'] == 1500
    assert by_type['excluded_transfers']['evidence']['excluded_amount'] == 54000
    assert by_type['unusual_transactions']['evidence']['count'] >= 1
    assert any('low confidence' in reason.lower() for reason in by_type['unusual_transactions']['reasons'])


