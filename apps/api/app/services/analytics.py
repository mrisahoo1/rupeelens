from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Transaction, Budget


def month_bounds(month: str):
    start = datetime.strptime(month + '-01', '%Y-%m-%d').date()
    end = datetime(start.year + (start.month // 12), (start.month % 12) + 1, 1).date()
    return start, end


def month_transactions(db: Session, user_id: int, month: str):
    start, end = month_bounds(month)
    return db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.transaction_date >= start, Transaction.transaction_date < end).all()


def summary(db: Session, user_id: int, month: str) -> dict:
    txs = month_transactions(db, user_id, month)
    spendable = [t for t in txs if not t.is_excluded_from_spend and not t.is_duplicate]
    debits = [t for t in spendable if t.direction == 'debit' and not t.is_refund]
    refunds = sum(t.amount for t in spendable if t.is_refund)
    by_cat = defaultdict(float); by_merch = defaultdict(float); by_mode = defaultdict(float); by_card = defaultdict(float); daily = defaultdict(float)
    weekend = 0.0; weekday = 0.0; low_confidence = 0
    for t in debits:
        by_cat[t.category] += t.amount; by_merch[t.merchant_normalized] += t.amount; by_mode[t.payment_mode] += t.amount; daily[t.transaction_date.isoformat()] += t.amount
        if t.transaction_date.weekday() >= 5: weekend += t.amount
        else: weekday += t.amount
        if (t.confidence_score or 0) < 0.55: low_confidence += 1
        if t.card_name: by_card[t.card_name] += t.amount
    total = sum(t.amount for t in debits) - refunds
    excluded = sum(t.amount for t in txs if t.is_excluded_from_spend)
    budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.month == month).all()
    overall_budget = next((b.amount for b in budgets if b.category == 'Overall'), 0)
    top_cat = max(by_cat.items(), key=lambda x: x[1], default=('Uncategorized', 0))
    top_merch = max(by_merch.items(), key=lambda x: x[1], default=('None', 0))
    return {'month': month, 'total_spend': round(total,2), 'credit_card_spend': round(by_mode['credit_card'],2), 'upi_spend': round(by_mode['upi'],2), 'manual_spend': round(by_mode['manual'] + by_mode['cash'],2), 'excluded_transfers': round(excluded,2), 'refunds': round(refunds,2), 'top_category': top_cat[0], 'top_merchant': top_merch[0], 'mom_change': 0, 'budget_progress': round((total / overall_budget) * 100, 1) if overall_budget else 0, 'category': dict(by_cat), 'merchant': dict(sorted(by_merch.items(), key=lambda x: x[1], reverse=True)[:10]), 'mode': dict(by_mode), 'card': dict(by_card), 'daily': dict(sorted(daily.items())), 'weekend_spend': round(weekend, 2), 'weekday_spend': round(weekday, 2), 'needs_revisit': len([t for t in txs if t.revisit_flag]), 'subscriptions': [m for m in by_merch if m.lower() in ['netflix','spotify','prime video','hotstar']], 'uncategorized': len([t for t in txs if t.category == 'Uncategorized']), 'low_confidence': low_confidence}


def build_insights(db: Session, user_id: int, month: str) -> list[dict]:
    data = summary(db, user_id, month)
    insights = []
    if data['total_spend'] <= 0:
        return [{'title': 'Blank canvas month', 'body': 'No included spend yet. Upload a statement and RupeeLens will start building your money map.', 'severity': 'info', 'emoji': '✨', 'metric': '0'}]
    if data['top_category'] != 'Uncategorized':
        insights.append({'title': f'{data["top_category"]} is driving the story', 'body': f'{data["top_category"]} is the lead category. Treat this as the first knob to turn before cutting everything randomly.', 'severity': 'info', 'emoji': '🎯', 'metric': data['top_category']})
    if data['upi_spend'] > 0:
        insights.append({'title': 'UPI confetti check', 'body': f'UPI spend is ₹{data["upi_spend"]:,.0f}. These quick taps are often where the month quietly leaks.', 'severity': 'warning', 'emoji': '🪄', 'metric': f'₹{data["upi_spend"]:,.0f}'})
    if data['excluded_transfers'] > 0:
        insights.append({'title': 'Noise removed from the lens', 'body': f'₹{data["excluded_transfers"]:,.0f} in transfers/card payments was excluded, so your spend number stays honest.', 'severity': 'positive', 'emoji': '🧹', 'metric': f'₹{data["excluded_transfers"]:,.0f}'})
    if data['subscriptions']:
        insights.append({'title': 'Subscription suspects spotted', 'body': ', '.join(data['subscriptions']) + ' look recurring. Keep, cancel, or downgrade them deliberately.', 'severity': 'info', 'emoji': '🔁', 'metric': str(len(data['subscriptions']))})
    if data['weekend_spend'] > data['weekday_spend'] * 0.35 and data['weekend_spend'] > 0:
        insights.append({'title': 'Weekend wallet weather', 'body': f'Weekends account for ₹{data["weekend_spend"]:,.0f}. That is where plans, food, and shopping may be clustering.', 'severity': 'info', 'emoji': '🌤️', 'metric': f'₹{data["weekend_spend"]:,.0f}'})
    if data['low_confidence']:
        insights.append({'title': 'Mystery transaction queue', 'body': f'{data["low_confidence"]} transactions have low parsing confidence. Fixing them improves every chart downstream.', 'severity': 'warning', 'emoji': '🕵️', 'metric': str(data['low_confidence'])})
    if data['uncategorized']:
        insights.append({'title': 'Uncategorized fog', 'body': f'{data["uncategorized"]} transactions need categories. One correction creates a merchant rule for next time.', 'severity': 'warning', 'emoji': '🌫️', 'metric': str(data['uncategorized'])})
    if data['budget_progress'] and data['budget_progress'] < 75:
        insights.append({'title': 'Budget breathing room', 'body': f'You have used {data["budget_progress"]}% of the overall budget. Keep the current pace and watch the top category.', 'severity': 'positive', 'emoji': '🟢', 'metric': f'{data["budget_progress"]}%'})
    return insights[:7]
