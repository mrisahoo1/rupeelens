from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class ConfidenceResult:
    score: float
    reasons: list[str]


def score_transaction_confidence(
    description: str,
    merchant: str,
    amount: float,
    transaction_date: date | None,
    direction: str,
    category: str,
    category_source: str,
    payment_mode: str,
    reference_id: str | None,
    is_duplicate: bool,
    is_excluded: bool,
) -> ConfidenceResult:
    score = 0.18
    reasons: list[str] = []
    description_text = (description or '').strip()
    merchant_text = (merchant or '').strip().lower()

    if transaction_date:
        score += 0.12
        reasons.append('Parsed transaction date')
    else:
        reasons.append('Missing transaction date')

    if amount and amount > 0:
        score += 0.12
        reasons.append('Valid amount')
    else:
        score -= 0.12
        reasons.append('Amount needs review')

    if description_text and len(description_text) >= 5:
        score += 0.08
    else:
        score -= 0.08
        reasons.append('Weak raw description')

    if merchant_text and merchant_text not in {'unknown merchant', 'unknown', 'transfer'}:
        score += 0.16
        reasons.append('Merchant extracted')
    else:
        score -= 0.14
        reasons.append('Needs merchant review')

    if category_source in {'rule', 'global_rule'}:
        score += 0.22
        reasons.append('Known merchant/category rule')
    elif category_source == 'manual':
        score += 0.2
        reasons.append('User-confirmed category')
    elif category != 'Uncategorized':
        score += 0.08
        reasons.append('Heuristic category match')
    else:
        score -= 0.16
        reasons.append('Uncategorized fallback')

    if payment_mode in {'upi', 'credit_card', 'bank'}:
        score += 0.08
        reasons.append('Recognized payment rail')
    if reference_id and str(reference_id).strip() not in {'', 'None', 'nan'}:
        score += 0.06
        reasons.append('Reference id present')
    if is_excluded:
        score += 0.04
        reasons.append('Exclusion rule matched')
    if direction not in {'debit', 'credit'}:
        score -= 0.1
        reasons.append('Direction unclear')
    if is_duplicate:
        score -= 0.22
        reasons.append('Potential duplicate')

    bounded = max(0.05, min(0.98, score))
    return ConfidenceResult(score=round(bounded, 2), reasons=reasons[:5])
