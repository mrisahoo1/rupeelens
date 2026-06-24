import csv
import re
from datetime import date

import pandas as pd
import pdfplumber

from .base import BaseParser, ParsedTransaction
from ..services.normalization import parse_amount, parse_date

DATE_KEYS = ['date', 'transaction date', 'txn date', 'tran date', 'value date']
POSTING_DATE_KEYS = ['posting date', 'post date', 'settlement date', 'value date']
DESC_KEYS = [
    'description', 'narration', 'details', 'transaction details', 'transaction remarks',
    'remarks', 'particulars', 'activity', 'merchant', 'payee payer', 'payee/payer',
    'payee', 'payer'
]
DEBIT_KEYS = ['debit', 'debit amount', 'withdrawal', 'withdrawal amt', 'withdrawal amount', 'paid out', 'money out', 'spent', 'dr']
CREDIT_KEYS = ['credit', 'credit amount', 'deposit', 'deposit amt', 'deposit amount', 'paid in', 'money in', 'received', 'cr']
AMOUNT_KEYS = ['amount', 'transaction amount', 'amount inr', 'amount (inr)', 'amount rs']
REF_KEYS = ['reference', 'reference no', 'ref no', 'utr', 'utr no', 'transaction id', 'txn id', 'rrn', 'wallet txn id', 'cheque/ref no']
DIRECTION_KEYS = ['type', 'txn type', 'transaction type', 'dr/cr', 'debit/credit', 'debit credit', 'cr/dr']


def _norm(value) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').strip().lower()).strip()


def _find(cols, keys):
    normalized = [(_norm(c), c) for c in cols]
    normalized_keys = [_norm(k) for k in keys]
    for key in normalized_keys:
        for low, original in normalized:
            tokens = low.split()
            if len(key) <= 2:
                if low == key or key in tokens:
                    return original
            elif low == key or low.endswith(f' {key}') or low.startswith(f'{key} ') or key in low:
                return original
    return None


def _value(row, col):
    if col is None:
        return None
    value = row.get(col)
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in {'', 'nan', 'none', 'null', '-'}:
        return None
    return value


def _text_value(row, col) -> str:
    value = _value(row, col)
    return '' if value is None else str(value).strip()


def _direction_from_text(*values) -> str | None:
    text = ' '.join(str(v or '') for v in values).lower()
    if re.search(r'\b(cr|credit|received|deposit|money in)\b', text):
        return 'credit'
    if re.search(r'\b(dr|debit|paid|spent|withdrawal|money out)\b', text):
        return 'debit'
    return None


def _amount_with_direction(value):
    text = str(value or '').strip()
    direction = _direction_from_text(text)
    amount = parse_amount(text)
    if amount < 0:
        direction = 'debit' if direction != 'credit' else 'credit'
        amount = abs(amount)
    return abs(amount), direction


def _read_csv(path: str) -> pd.DataFrame:
    with open(path, newline='', encoding='utf-8-sig') as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return pd.DataFrame()
    header = [cell.strip() for cell in rows[0]]
    data = rows[1:]
    normalized_header = [_norm(cell) for cell in header]
    if 'transaction details' in normalized_header and 'type' in normalized_header and 'amount' in normalized_header:
        type_index = normalized_header.index('type')
        repaired_header = header[:type_index] + ['VPA'] + header[type_index:]
        repaired_rows = []
        for row in data:
            if len(row) == len(repaired_header):
                repaired_rows.append(row)
            elif len(row) == len(header):
                repaired_rows.append(row[:type_index] + [''] + row[type_index:])
            else:
                repaired_rows.append(row[:len(repaired_header)])
        return pd.DataFrame(repaired_rows, columns=repaired_header)
    return pd.read_csv(path, dtype=str, engine='python', encoding='utf-8-sig', on_bad_lines='skip')


class DataFrameParser(BaseParser):
    def rows_from_df(self, df: pd.DataFrame, source_type: str) -> list[ParsedTransaction]:
        df = _prepare_df(df)
        if df.empty:
            return []

        date_col = _find(df.columns, DATE_KEYS)
        posting_col = _find(df.columns, POSTING_DATE_KEYS)
        if posting_col == date_col:
            posting_col = _find([c for c in df.columns if c != date_col], POSTING_DATE_KEYS)
        desc_col = _find(df.columns, DESC_KEYS)
        debit_col = _find(df.columns, DEBIT_KEYS)
        credit_col = _find(df.columns, CREDIT_KEYS)
        amount_col = _find(df.columns, AMOUNT_KEYS)
        ref_col = _find(df.columns, REF_KEYS)
        direction_col = _find(df.columns, DIRECTION_KEYS)

        if not date_col or not desc_col:
            raise ValueError('Could not infer date and description columns')

        parsed = []
        for _, row in df.iterrows():
            try:
                debit = parse_amount(_value(row, debit_col)) if _value(row, debit_col) is not None else 0
                credit = parse_amount(_value(row, credit_col)) if _value(row, credit_col) is not None else 0
                amount = 0.0
                direction = _direction_from_text(_value(row, direction_col))

                if debit:
                    amount = abs(debit)
                    direction = 'debit'
                elif credit:
                    amount = abs(credit)
                    direction = 'credit'
                elif amount_col:
                    amount, amount_direction = _amount_with_direction(_value(row, amount_col))
                    direction = direction or amount_direction or 'debit'

                if not amount:
                    continue

                raw_description = _text_value(row, desc_col)
                reference = _text_value(row, ref_col) or None
                parsed.append(
                    ParsedTransaction(
                        transaction_date=parse_date(row[date_col]),
                        posting_date=parse_date(row[posting_col]) if posting_col and _value(row, posting_col) is not None else None,
                        description_raw=raw_description,
                        amount=abs(amount),
                        direction=direction or 'debit',
                        merchant_raw=raw_description,
                        reference_id=reference,
                        payment_mode=_mode(source_type),
                    )
                )
            except Exception:
                continue
        return parsed


def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how='all').copy()
    df.columns = [str(c).strip() for c in df.columns]
    unnamed = [c for c in df.columns if str(c).lower().startswith('unnamed')]
    if unnamed:
        df = df.drop(columns=unnamed)
    return df


def _mode(source_type: str) -> str:
    value = source_type.lower()
    if 'upi' in value: return 'upi'
    if 'credit' in value or 'card' in value: return 'credit_card'
    if 'bank' in value: return 'bank'
    return 'manual'


class CSVParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        return self.rows_from_df(_read_csv(path), source_type)


class XLSXParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        return self.rows_from_df(pd.read_excel(path, dtype=str), source_type)


class PDFParser(DataFrameParser):
    def parse(self, path: str, source_type: str):
        rows = []
        line_re = re.compile(r'^(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})\s+(?P<body>.+?)\s+(?P<amount>[\(]?[₹RsINR\s,.\d-]+[\)]?\s*(?:Cr|CR|Dr|DR)?)\s*(?P<ref>[A-Z0-9-]{4,})?$')
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                for line in text.splitlines():
                    match = line_re.match(line.strip())
                    if not match:
                        continue
                    rows.append({
                        'date': match.group('date'),
                        'description': match.group('body').strip(),
                        'amount': match.group('amount').strip(),
                        'reference': match.group('ref'),
                    })
        return self.rows_from_df(pd.DataFrame(rows), source_type)


def parser_for(filename: str) -> BaseParser:
    low = filename.lower()
    if low.endswith('.csv'): return CSVParser()
    if low.endswith(('.xlsx', '.xls')): return XLSXParser()
    if low.endswith('.pdf'): return PDFParser()
    raise ValueError('Unsupported file type')
