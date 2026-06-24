import pandas as pd
import pdfplumber
from .base import BaseParser, ParsedTransaction
from ..services.normalization import parse_amount, parse_date

DATE_KEYS = ['date','transaction date','txn date','value date']
DESC_KEYS = ['description','narration','details','transaction details','merchant']
DEBIT_KEYS = ['debit','withdrawal','paid out','dr']
CREDIT_KEYS = ['credit','deposit','paid in','cr']
AMOUNT_KEYS = ['amount','transaction amount']
REF_KEYS = ['reference','ref no','utr','transaction id']

def _find(cols, keys):
    lowered = {str(c).strip().lower(): c for c in cols}
    for key in keys:
        for low, original in lowered.items():
            if key in low:
                return original
    return None

class DataFrameParser(BaseParser):
    def rows_from_df(self, df: pd.DataFrame, source_type: str) -> list[ParsedTransaction]:
        df = df.dropna(how='all')
        date_col = _find(df.columns, DATE_KEYS)
        desc_col = _find(df.columns, DESC_KEYS)
        debit_col = _find(df.columns, DEBIT_KEYS)
        credit_col = _find(df.columns, CREDIT_KEYS)
        amount_col = _find(df.columns, AMOUNT_KEYS)
        ref_col = _find(df.columns, REF_KEYS)
        if not date_col or not desc_col:
            raise ValueError('Could not infer date and description columns')
        parsed = []
        for _, row in df.iterrows():
            try:
                debit = parse_amount(row.get(debit_col)) if debit_col else 0
                credit = parse_amount(row.get(credit_col)) if credit_col else 0
                amount = parse_amount(row.get(amount_col)) if amount_col else (debit or credit)
                direction = 'credit' if credit and not debit else 'debit'
                if amount < 0:
                    direction, amount = 'credit', abs(amount)
                parsed.append(ParsedTransaction(transaction_date=parse_date(row[date_col]), description_raw=str(row[desc_col]), amount=abs(amount), direction=direction, merchant_raw=str(row.get(desc_col)), reference_id=str(row.get(ref_col)) if ref_col else None, payment_mode=_mode(source_type)))
            except Exception:
                continue
        return parsed

def _mode(source_type: str) -> str:
    value = source_type.lower()
    if 'upi' in value: return 'upi'
    if 'credit' in value or 'card' in value: return 'credit_card'
    if 'bank' in value: return 'bank'
    return 'manual'

class CSVParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        return self.rows_from_df(pd.read_csv(path), source_type)

class XLSXParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        return self.rows_from_df(pd.read_excel(path), source_type)

class PDFParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        rows = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                for line in text.splitlines():
                    parts = line.split()
                    if len(parts) >= 4 and any(ch.isdigit() for ch in parts[0]):
                        rows.append({'date': parts[0], 'description': ' '.join(parts[1:-1]), 'amount': parts[-1]})
        return self.rows_from_df(pd.DataFrame(rows), source_type)

def parser_for(filename: str) -> BaseParser:
    low = filename.lower()
    if low.endswith('.csv'): return CSVParser()
    if low.endswith(('.xlsx', '.xls')): return XLSXParser()
    if low.endswith('.pdf'): return PDFParser()
    raise ValueError('Unsupported file type')
