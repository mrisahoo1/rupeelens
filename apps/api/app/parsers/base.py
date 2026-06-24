from dataclasses import dataclass
from datetime import date

@dataclass
class ParsedTransaction:
    transaction_date: date
    description_raw: str
    amount: float
    direction: str
    merchant_raw: str | None = None
    posting_date: date | None = None
    reference_id: str | None = None
    payment_mode: str = 'manual'

class BaseParser:
    def parse(self, path: str, source_type: str) -> list[ParsedTransaction]:
        raise NotImplementedError
