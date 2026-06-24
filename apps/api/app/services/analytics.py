from collections import defaultdict
from datetime import datetime
from statistics import mean, pstdev
from sqlalchemy.orm import Session
from ..models import Transaction, Budget


def month_bounds(month: str):
    start = datetime.strptime(month + '-01', '%Y-%m-%d').date()
    end = datetime(start.year + (start.month // 12), (start.month % 12) + 1, 1).date()
    return start, end


def previous_month(month: str) -> str:
    start, _ = month_bounds(month)
    year = start.year if start.month > 1 else start.year - 1
    month_num = start.month - 1 if start.month > 1 else 12
    return f'{year:04d}-{month_num:02d}'


def month_transactions(db: Session, user_id: int, month: str):
    start, end = month_bounds(month)
    return db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.transaction_date >= start, Transaction.transaction_date < end).all()


def _included_debits(txs):
    return [t for t in txs if not t.is_excluded_from_spend and not t.is_duplicate and t.direction == 'debit' and not t.is_refund]


def _refunds(txs):
    return [t for t in txs if not t.is_excluded_from_spend and not t.is_duplicate and t.is_refund]


def _money(value) -> str:
    return f'₹{value:,.0f}'


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.75:
        return 'high'
    if confidence >= 0.5:
        return 'medium'
    return 'low'


def _insight(type_: str, title: str, body: str, severity: str, emoji: str, metric: str, confidence: float, reasons: list[str], evidence: dict) -> dict:
    confidence = max(0.0, min(1.0, round(confidence, 2)))
    return {
        'type': type_,
        'title': title,
        'body': body,
        'severity': severity,
        'emoji': emoji,
        'metric': metric,
        'confidence': confidence,
        'confidence_label': _confidence_label(confidence),
        'reasons': reasons,
        'evidence': evidence,
    }


def _sum_by(items, attr):
    bucket = defaultdict(float)
    for item in items:
        bucket[getattr(item, attr)] += item.amount
    return bucket


def _budget_lookup(db: Session, user_id: int, month: str):
    return {b.category: b.amount for b in db.query(Budget).filter(Budget.user_id == user_id, Budget.month == month).all()}


def summary(db: Session, user_id: int, month: str) -> dict:
    txs = month_transactions(db, user_id, month)
    debits = _included_debits(txs)
    refunds = sum(t.amount for t in _refunds(txs))
    by_cat = defaultdict(float); by_merch = defaultdict(float); by_mode = defaultdict(float); by_card = defaultdict(float); daily = defaultdict(float)
    weekend = 0.0; weekday = 0.0; low_confidence = 0
    for t in debits:
        by_cat[t.category] += t.amount; by_merch[t.merchant_normalized] += t.amount; by_mode[t.payment_mode] += t.amount; daily[t.transaction_date.isoformat()] += t.amount
        if t.transaction_date.weekday() >= 5: weekend += t.amount
        else: weekday += t.amount
        if (t.confidence_score or 0) < 0.55: low_confidence += 1
        if t.card_name: by_card[t.card_name] += t.amount
    total = sum(t.amount for t in debits) - refunds
    excluded = sum(t.amount for t in txs if t.is_excluded_from_spend and not t.is_duplicate)
    budgets = _budget_lookup(db, user_id, month)
    overall_budget = budgets.get('Overall', 0)
    top_cat = max(by_cat.items(), key=lambda x: x[1], default=('Uncategorized', 0))
    top_merch = max(by_merch.items(), key=lambda x: x[1], default=('None', 0))
    return {'month': month, 'total_spend': round(total,2), 'credit_card_spend': round(by_mode['credit_card'],2), 'upi_spend': round(by_mode['upi'],2), 'manual_spend': round(by_mode['manual'] + by_mode['cash'],2), 'excluded_transfers': round(excluded,2), 'refunds': round(refunds,2), 'top_category': top_cat[0], 'top_merchant': top_merch[0], 'mom_change': 0, 'budget_progress': round((total / overall_budget) * 100, 1) if overall_budget else 0, 'category': dict(by_cat), 'merchant': dict(sorted(by_merch.items(), key=lambda x: x[1], reverse=True)[:10]), 'mode': dict(by_mode), 'card': dict(by_card), 'daily': dict(sorted(daily.items())), 'weekend_spend': round(weekend, 2), 'weekday_spend': round(weekday, 2), 'needs_revisit': len([t for t in txs if t.revisit_flag]), 'subscriptions': [m for m in by_merch if m.lower() in ['netflix','spotify','prime video','hotstar']], 'uncategorized': len([t for t in txs if t.category == 'Uncategorized']), 'low_confidence': low_confidence}


def build_insights(db: Session, user_id: int, month: str) -> list[dict]:
    current_txs = month_transactions(db, user_id, month)
    current_debits = _included_debits(current_txs)
    current_refunds = _refunds(current_txs)
    total_spend = sum(t.amount for t in current_debits) - sum(t.amount for t in current_refunds)
    if total_spend <= 0 and not current_txs:
        return [_insight('empty_month', 'Blank canvas month', 'No included spend yet. Upload a statement and RupeeLens will start building your money map.', 'info', '✨', '0', 0.95, ['No transactions were found for this user and month.'], {'month': month, 'transaction_count': 0})]

    insights = []
    prev_txs = month_transactions(db, user_id, previous_month(month))
    prev_debits = _included_debits(prev_txs)
    current_by_cat = _sum_by(current_debits, 'category')
    prev_by_cat = _sum_by(prev_debits, 'category')
    current_by_merchant = _sum_by(current_debits, 'merchant_normalized')
    budgets = _budget_lookup(db, user_id, month)

    insights.extend(_category_spike(current_by_cat, prev_by_cat, month))
    insights.extend(_small_upi_impulse(current_debits))
    insights.extend(_recurring_subscriptions(current_debits))
    insights.extend(_weekend_spending(current_debits))
    insights.extend(_merchant_concentration(current_by_merchant, sum(t.amount for t in current_debits)))
    insights.extend(_budget_risk(current_by_cat, total_spend, budgets))
    insights.extend(_refund_summary(current_refunds))
    insights.extend(_excluded_transfers(current_txs))
    insights.extend(_unusual_transactions(current_debits))

    if not insights:
        insights.append(_insight('steady_month', 'Nothing dramatic this month', 'No strong spikes, concentration risks, refund patterns, or unusual transactions crossed the deterministic thresholds.', 'positive', '🟢', 'steady', 0.7, ['All insight rules ran, but no rule crossed its threshold.'], {'month': month, 'included_transaction_count': len(current_debits)}))
    return sorted(insights, key=lambda item: _severity_rank(item['severity']), reverse=True)


def _severity_rank(severity: str) -> int:
    return {'danger': 4, 'warning': 3, 'info': 2, 'positive': 1}.get(severity, 0)


def _category_spike(current_by_cat, prev_by_cat, month):
    candidates = []
    for category, current in current_by_cat.items():
        previous = prev_by_cat.get(category, 0)
        if previous < 1000 or current < 1500:
            continue
        increase = current - previous
        pct = (increase / previous) * 100 if previous else 0
        if increase >= 1000 and pct >= 35:
            candidates.append((pct, increase, category, current, previous))
    if not candidates:
        return []
    pct, increase, category, current, previous = max(candidates, key=lambda item: (item[0], item[1]))
    confidence = 0.88 if previous >= 1500 else 0.72
    return [_insight('category_spike', f'{category} jumped this month', f'{category} is up {pct:.0f}% versus last month, adding {_money(increase)} of extra spend pressure.', 'warning', '📈', f'+{pct:.0f}%', confidence, [f'Current {category} spend is {_money(current)}.', f'Previous month {category} spend was {_money(previous)}.', 'The increase crossed both the 35% and ₹1,000 thresholds.'], {'month': month, 'category': category, 'current_amount': round(current, 2), 'previous_amount': round(previous, 2), 'increase_amount': round(increase, 2), 'increase_pct': round(pct, 1), 'thresholds': {'min_increase_pct': 35, 'min_increase_amount': 1000}})]


def _small_upi_impulse(debits):
    small = [t for t in debits if t.payment_mode == 'upi' and t.amount <= 300]
    amount = sum(t.amount for t in small)
    if len(small) < 3 or amount < 300:
        return []
    return [_insight('small_upi_impulse', 'Small UPI taps are adding up', f'{len(small)} UPI payments under ₹300 added up to {_money(amount)}. These are easy to miss because each one feels harmless.', 'warning', '⚡', f'{len(small)} taps', 0.9, [f'Found {len(small)} included UPI debits at or below ₹300.', f'Together they total {_money(amount)}.', 'Credit card payments and transfers were excluded before this check.'], {'count': len(small), 'amount': round(amount, 2), 'threshold_amount': 300, 'payment_mode': 'upi', 'sample_merchants': [t.merchant_normalized for t in small[:5]]})]


def _recurring_subscriptions(debits):
    by_merchant = defaultdict(list)
    for t in debits:
        if t.category == 'Subscriptions' or t.merchant_normalized.lower() in {'netflix', 'spotify', 'prime video', 'hotstar'}:
            by_merchant[t.merchant_normalized].append(t)
    candidates = [(merchant, rows) for merchant, rows in by_merchant.items() if len(rows) >= 2]
    if not candidates:
        return []
    merchant, rows = max(candidates, key=lambda item: (len(item[1]), sum(t.amount for t in item[1])))
    amount = sum(t.amount for t in rows)
    return [_insight('recurring_subscription', f'{merchant} looks recurring', f'{merchant} appears {len(rows)} times in subscription-like spend this month, totaling {_money(amount)}.', 'info', '🔁', str(len(rows)), 0.86, [f'{len(rows)} included transactions matched the same subscription merchant.', 'The merchant is categorized as Subscriptions or is in the known subscription merchant list.', 'Excluded transfers and duplicates were ignored.'], {'merchant': merchant, 'count': len(rows), 'amount': round(amount, 2), 'dates': [t.transaction_date.isoformat() for t in rows]})]


def _weekend_spending(debits):
    total = sum(t.amount for t in debits)
    if total <= 0:
        return []
    weekend = sum(t.amount for t in debits if t.transaction_date.weekday() >= 5)
    share = weekend / total
    if weekend < 1500 or share < 0.35:
        return []
    severity = 'warning' if share >= 0.5 else 'info'
    return [_insight('weekend_spending', 'Weekend spending is carrying the month', f'Weekend transactions account for {share * 100:.0f}% of included spend, or {_money(weekend)}.', severity, '🌤️', f'{share * 100:.0f}%', 0.82, [f'Weekend spend is {_money(weekend)}.', f'Total included debit spend before refunds is {_money(total)}.', 'The weekend share crossed the 35% threshold.'], {'weekend_amount': round(weekend, 2), 'total_debit_amount': round(total, 2), 'weekend_share': round(share, 3), 'threshold_share': 0.35})]


def _merchant_concentration(by_merchant, debit_total):
    if debit_total <= 0 or not by_merchant:
        return []
    merchant, amount = max(by_merchant.items(), key=lambda item: item[1])
    share = amount / debit_total
    if amount < 5000 or share < 0.25:
        return []
    severity = 'warning' if share >= 0.4 else 'info'
    return [_insight('merchant_concentration', f'{merchant} dominates merchant spend', f'{merchant} alone represents {share * 100:.0f}% of included debit spend.', severity, '🏦', f'{share * 100:.0f}%', 0.84, [f'{merchant} is the largest merchant by included debit spend.', f'Its spend is {_money(amount)} out of {_money(debit_total)}.', 'The top-merchant share crossed the 25% concentration threshold.'], {'merchant': merchant, 'amount': round(amount, 2), 'total_debit_amount': round(debit_total, 2), 'share': round(share, 3), 'threshold_share': 0.25})]


def _budget_risk(current_by_cat, total_spend, budgets):
    selected = None
    if budgets.get('Overall'):
        used = total_spend / budgets['Overall']
        if used >= 0.8:
            selected = ('Overall', total_spend, budgets['Overall'], used)
    if selected is None:
        risks = []
        for category, budget in budgets.items():
            if category == 'Overall' or not budget:
                continue
            amount = current_by_cat.get(category, 0)
            used = amount / budget
            if used >= 0.8:
                risks.append((category, amount, budget, used))
        if risks:
            selected = max(risks, key=lambda item: item[3])
    if selected is None:
        return []
    category, amount, budget, used = selected
    severity = 'danger' if used >= 1 else 'warning'
    return [_insight('budget_risk', f'{category} budget is at risk', f'{category} has used {used * 100:.0f}% of its monthly budget.', severity, '🚦', f'{used * 100:.0f}%', 0.91, [f'{category} spend is {_money(amount)}.', f'The configured budget is {_money(budget)}.', 'The budget usage crossed the 80% risk threshold.'], {'category': category, 'current_amount': round(amount, 2), 'budget_amount': round(budget, 2), 'usage_pct': round(used * 100, 1), 'threshold_pct': 80})]


def _refund_summary(refunds):
    amount = sum(t.amount for t in refunds)
    if amount <= 0:
        return []
    return [_insight('refunds', 'Refunds softened the month', f'{len(refunds)} refund or reversal entries reduced net spend by {_money(amount)}.', 'positive', '↩️', _money(amount), 0.88, [f'Found {len(refunds)} included refund/reversal transactions.', f'Total refund amount is {_money(amount)}.', 'Refunds are shown separately and reduce net spend.'], {'count': len(refunds), 'refund_amount': round(amount, 2), 'merchants': [t.merchant_normalized for t in refunds[:5]]})]


def _excluded_transfers(txs):
    excluded = [t for t in txs if t.is_excluded_from_spend and not t.is_duplicate]
    amount = sum(t.amount for t in excluded)
    if amount <= 0:
        return []
    cc_amount = sum(t.amount for t in excluded if t.is_credit_card_payment)
    transfer_amount = sum(t.amount for t in excluded if t.is_transfer)
    return [_insight('excluded_transfers', 'Transfers were removed from actual spend', f'{_money(amount)} in card payments, self-transfers, or wallet-load style movement was excluded from expense totals.', 'positive', '🧹', _money(amount), 0.93, [f'Excluded transaction total is {_money(amount)}.', f'Credit card payment portion is {_money(cc_amount)}.', f'Transfer/self-transfer portion is {_money(transfer_amount)}.'], {'count': len(excluded), 'excluded_amount': round(amount, 2), 'credit_card_payment_amount': round(cc_amount, 2), 'transfer_amount': round(transfer_amount, 2)})]


def _unusual_transactions(debits):
    if not debits:
        return []
    amounts = [t.amount for t in debits]
    avg = mean(amounts)
    spread = pstdev(amounts) if len(amounts) > 1 else 0
    threshold = max(avg + (2 * spread), avg * 2.5, 5000)
    unusual = [t for t in debits if t.amount >= threshold]
    low_confidence = [t for t in debits if (t.confidence_score or 0) < 0.55]
    combined = {t.id or id(t): t for t in unusual + low_confidence}
    rows = list(combined.values())
    if not rows:
        return []
    reasons = []
    if unusual:
        reasons.append(f'{len(unusual)} included debit transaction crossed the unusual amount threshold of {_money(threshold)}.')
    if low_confidence:
        reasons.append(f'{len(low_confidence)} transaction has low confidence below 55%.')
    reasons.append('Excluded transfers, card payments, duplicates, and refunds were ignored for this check.')
    confidence = 0.76 if unusual and low_confidence else 0.64
    return [_insight('unusual_transactions', 'Transactions need a closer look', f'{len(rows)} transactions look unusual by amount or parsing confidence.', 'warning', '🕵️', str(len(rows)), confidence, reasons, {'count': len(rows), 'amount_threshold': round(threshold, 2), 'average_amount': round(avg, 2), 'low_confidence_count': len(low_confidence), 'large_transaction_count': len(unusual), 'transactions': [{'date': t.transaction_date.isoformat(), 'merchant': t.merchant_normalized, 'amount': round(t.amount, 2), 'confidence_score': round(t.confidence_score or 0, 2)} for t in rows[:8]]})]
