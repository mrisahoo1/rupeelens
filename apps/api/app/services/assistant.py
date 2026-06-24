import json
import urllib.error
import urllib.request
from collections import defaultdict
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models import Transaction, Budget
from .analytics import summary, build_insights, month_transactions


def _compact_money(value: float) -> str:
    return f'₹{value:,.0f}'


def _context(db: Session, user_id: int, month: str) -> dict:
    data = summary(db, user_id, month)
    txs = month_transactions(db, user_id, month)
    budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.month == month).all()
    by_category = sorted(data['category'].items(), key=lambda item: item[1], reverse=True)
    small_upi = sum(t.amount for t in txs if t.payment_mode == 'upi' and t.amount <= 300 and not t.is_excluded_from_spend and t.direction == 'debit')
    return {
        'month': month,
        'total_spend': data['total_spend'],
        'excluded_transfers': data['excluded_transfers'],
        'refunds': data['refunds'],
        'top_category': data['top_category'],
        'top_merchant': data['top_merchant'],
        'budget_progress': data['budget_progress'],
        'budgets': [{'category': b.category, 'amount': b.amount} for b in budgets],
        'top_categories': by_category[:5],
        'top_merchants': list(data['merchant'].items())[:5],
        'small_upi_total': round(small_upi, 2),
        'uncategorized': data['uncategorized'],
        'needs_revisit': data['needs_revisit'],
        'insights': build_insights(db, user_id, month),
    }


def deterministic_answer(context: dict, question: str) -> dict:
    q = question.lower()
    cards = [
        {'label': 'Spend', 'value': _compact_money(context['total_spend'])},
        {'label': 'Budget used', 'value': f"{context['budget_progress']}%"},
        {'label': 'Top category', 'value': context['top_category']},
    ]
    if 'budget' in q:
        if context['budget_progress'] == 0:
            answer = 'No overall budget is set for this month yet. Add an Overall budget first, then category budgets for the 2-3 areas you want to control.'
        elif context['budget_progress'] >= 100:
            answer = f"You are over the monthly budget line at {context['budget_progress']}%. Freeze discretionary categories and review {context['top_category']} first."
        elif context['budget_progress'] >= 80:
            answer = f"You have used {context['budget_progress']}% of budget. Keep an eye on {context['top_category']} and avoid small impulse UPI spends for the rest of the month."
        else:
            answer = f"Budget health looks manageable at {context['budget_progress']}% used. The next lever is {context['top_category']}, not transfers or card payments."
    elif 'upi' in q:
        answer = f"UPI small-spend leakage is {_compact_money(context['small_upi_total'])}. These are the easy-to-miss payments; scan them before changing big budgets."
        cards.append({'label': 'Small UPI', 'value': _compact_money(context['small_upi_total'])})
    elif 'merchant' in q or 'where' in q:
        merchants = ', '.join([f"{name} ({_compact_money(value)})" for name, value in context['top_merchants'][:3]]) or 'no merchants yet'
        answer = f"Your biggest merchant signals are {merchants}. This is based only on included spend, so card payments and transfers are not inflating it."
    else:
        answer = f"For {context['month']}, actual spend is {_compact_money(context['total_spend'])}. {context['top_category']} is the lead category and {context['top_merchant']} is the lead merchant. Ask about budget, UPI, merchants, or categories for a sharper answer."
    return {'answer': answer, 'cards': cards, 'mode': 'deterministic', 'context': context}


def ollama_answer(context: dict, question: str) -> str | None:
    settings = get_settings()
    if not getattr(settings, 'enable_ollama_insights', False):
        return None
    payload = {
        'model': settings.ollama_model,
        'stream': False,
        'messages': [
            {'role': 'system', 'content': 'You are RupeeLens, a concise Indian personal finance analyst. Use only the provided JSON context. Never invent transactions.'},
            {'role': 'user', 'content': f'Context JSON: {json.dumps(context, ensure_ascii=False)}\nQuestion: {question}'},
        ],
    }
    req = urllib.request.Request(
        settings.ollama_url.rstrip('/') + '/api/chat',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=settings.ollama_timeout_seconds) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('message', {}).get('content')
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def answer_spend_question(db: Session, user_id: int, month: str, question: str) -> dict:
    context = _context(db, user_id, month)
    base = deterministic_answer(context, question)
    generated = ollama_answer(context, question)
    if generated:
        base['answer'] = generated
        base['mode'] = 'ollama'
    return base
