from datetime import date

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.parsers.generic import CSVParser, XLSXParser, PDFParser
from app.services.normalization import classify_flags, clean_merchant


def _write_pdf(path, lines):
    c = canvas.Canvas(str(path), pagesize=A4)
    y = 800
    for line in lines:
        c.drawString(40, y, line)
        y -= 18
    c.save()


def test_hdfc_credit_card_csv_parses_debit_and_bill_payment(tmp_path):
    path = tmp_path / 'hdfc_card.csv'
    path.write_text(
        'Transaction Date,Post Date,Description,Debit Amount,Credit Amount,Ref No.\n'
        '12/06/2026,13/06/2026,UPI/ZOMATO/9876543210/zomato@axis,542.50,,HDFC001\n'
        '15/06/2026,15/06/2026,CRED CC PAYMENT THANK YOU,48000,,HDFC002\n',
        encoding='utf-8',
    )

    rows = CSVParser().parse(str(path), 'Credit Card CSV/XLSX')

    assert len(rows) == 2
    assert rows[0].transaction_date == date(2026, 6, 12)
    assert rows[0].posting_date == date(2026, 6, 13)
    assert rows[0].direction == 'debit'
    assert rows[0].amount == 542.5
    assert rows[0].payment_mode == 'credit_card'
    assert clean_merchant(rows[0].description_raw) == 'Zomato'
    flags = classify_flags(rows[1].description_raw, rows[1].direction, rows[1].amount)
    assert flags['is_credit_card_payment']
    assert flags['is_excluded_from_spend']


def test_icici_credit_card_xlsx_parses_credits_as_refunds(tmp_path):
    path = tmp_path / 'icici_card.xlsx'
    df = pd.DataFrame(
        [
            {'Txn Date': '05-Jun-2026', 'Value Date': '06-Jun-2026', 'Transaction Remarks': 'AMZN Mktp IN', 'Withdrawal Amt.': '1,999.00', 'Deposit Amt.': '', 'Reference No': 'ICICI001'},
            {'Txn Date': '08-Jun-2026', 'Value Date': '08-Jun-2026', 'Transaction Remarks': 'Amazon Refund Reversal', 'Withdrawal Amt.': '', 'Deposit Amt.': '799.00', 'Reference No': 'ICICI002'},
        ]
    )
    df.to_excel(path, index=False)

    rows = XLSXParser().parse(str(path), 'Credit Card CSV/XLSX')

    assert len(rows) == 2
    assert rows[0].direction == 'debit'
    assert rows[0].amount == 1999
    assert clean_merchant(rows[0].description_raw) == 'Amazon'
    assert rows[1].direction == 'credit'
    refund_flags = classify_flags(rows[1].description_raw, rows[1].direction, rows[1].amount)
    assert refund_flags['is_refund']
    assert not refund_flags['is_excluded_from_spend']


def test_sbi_axis_amex_style_amount_signs_and_cr_dr_suffixes(tmp_path):
    sbi = tmp_path / 'sbi_card.csv'
    sbi.write_text(
        'Date,Description,Amount\n'
        '10/06/2026,SWIGGY PAYMENTS,299.00 Dr\n'
        '11/06/2026,MERCHANT REVERSAL,150.00 Cr\n',
        encoding='utf-8',
    )
    axis = tmp_path / 'axis_card.csv'
    axis.write_text(
        'Tran Date,Particulars,Amount (INR),Dr/Cr\n'
        '12-06-2026,AXIS CARD PAYMENT RECEIVED,25000,DR\n',
        encoding='utf-8',
    )
    amex = tmp_path / 'amex.csv'
    amex.write_text(
        'Date,Description,Amount\n'
        '2026-06-14,UBER TRIP,-421.75\n'
        '2026-06-16,AMEX PAYMENT RECEIVED,35000 CR\n',
        encoding='utf-8',
    )

    sbi_rows = CSVParser().parse(str(sbi), 'Credit Card CSV/XLSX')
    axis_rows = CSVParser().parse(str(axis), 'Credit Card CSV/XLSX')
    amex_rows = CSVParser().parse(str(amex), 'Credit Card CSV/XLSX')

    assert [row.direction for row in sbi_rows] == ['debit', 'credit']
    assert sbi_rows[0].amount == 299
    assert classify_flags(sbi_rows[1].description_raw, sbi_rows[1].direction, sbi_rows[1].amount)['is_refund']
    assert classify_flags(axis_rows[0].description_raw, axis_rows[0].direction, axis_rows[0].amount)['is_credit_card_payment']
    assert amex_rows[0].direction == 'debit'
    assert clean_merchant(amex_rows[0].description_raw) == 'Uber'
    assert classify_flags(amex_rows[1].description_raw, amex_rows[1].direction, amex_rows[1].amount)['is_credit_card_payment']


def test_phonepe_googlepay_paytm_bhim_upi_exports_detect_transfers_wallet_loads_and_spends(tmp_path):
    phonepe = tmp_path / 'phonepe.csv'
    phonepe.write_text(
        'Transaction Date,Transaction Details,Type,Amount,UTR No.\n'
        '2026-06-01,Paid to Zomato,zomato@axis,DEBIT,321,UTR001\n'
        '2026-06-02,Received from Rahul,rahul@okicici,CREDIT,500,UTR002\n'
        '2026-06-03,Added money to Paytm Wallet,DEBIT,1000,UTR003\n',
        encoding='utf-8',
    )
    gpay = tmp_path / 'gpay.csv'
    gpay.write_text(
        'Date,Description,Amount (INR),Debit/Credit,Transaction ID\n'
        '03 Jun 2026,Paid to Swiggy Payments,249,Debit,GPAY001\n'
        '04 Jun 2026,Self transfer to HDFC Bank,5000,Debit,GPAY002\n',
        encoding='utf-8',
    )
    paytm = tmp_path / 'paytm.csv'
    paytm.write_text(
        'Date,Activity,Money Out,Money In,Wallet Txn ID\n'
        '05/06/2026,Paid for BookMyShow,650,,PAYTM001\n'
        '06/06/2026,Refund from Paytm Mall,,399,PAYTM002\n',
        encoding='utf-8',
    )
    bhim = tmp_path / 'bhim.csv'
    bhim.write_text(
        'Txn Date,Payee/Payer,Txn Type,Amount,RRN\n'
        '07-06-2026,IRCTC UPI,DEBIT,1420,BHIM001\n'
        '08-06-2026,Own Account Transfer,DEBIT,9000,BHIM002\n',
        encoding='utf-8',
    )

    rows = []
    for path in [phonepe, gpay, paytm, bhim]:
        rows.extend(CSVParser().parse(str(path), 'UPI CSV/XLSX'))

    by_ref = {row.reference_id: row for row in rows}
    assert by_ref['UTR001'].payment_mode == 'upi'
    assert by_ref['UTR001'].direction == 'debit'
    assert clean_merchant(by_ref['UTR001'].description_raw) == 'Zomato'
    assert by_ref['UTR002'].direction == 'credit'
    assert classify_flags(by_ref['UTR003'].description_raw, by_ref['UTR003'].direction, by_ref['UTR003'].amount)['is_transfer']
    assert classify_flags(by_ref['GPAY002'].description_raw, by_ref['GPAY002'].direction, by_ref['GPAY002'].amount)['is_transfer']
    assert clean_merchant(by_ref['PAYTM001'].description_raw) == 'BookMyShow'
    assert classify_flags(by_ref['PAYTM002'].description_raw, by_ref['PAYTM002'].direction, by_ref['PAYTM002'].amount)['is_refund']
    assert clean_merchant(by_ref['BHIM001'].description_raw) == 'IRCTC'
    assert classify_flags(by_ref['BHIM002'].description_raw, by_ref['BHIM002'].direction, by_ref['BHIM002'].amount)['is_transfer']


def test_bank_statement_and_pdf_parser_handle_common_patterns(tmp_path):
    bank = tmp_path / 'bank.csv'
    bank.write_text(
        'Value Date,Narration,Withdrawal,Deposit,Cheque/Ref No\n'
        '09/06/2026,NEFT SELF TRANSFER TO OWN ACCOUNT,10000,,BNK001\n'
        '10/06/2026,UPI/Airtel/BILLPAY/airtel@upi,799,,BNK002\n'
        '11/06/2026,CASHBACK REVERSAL,,50,BNK003\n',
        encoding='utf-8',
    )
    pdf_path = tmp_path / 'hdfc_statement.pdf'
    _write_pdf(
        pdf_path,
        [
            'Date Description Debit Credit Ref No',
            '12/06/2026 UPI/ZEPTO/ORDER123/zepto@upi 432.10 Dr PDF001',
            '13/06/2026 HDFC CREDIT CARD PAYMENT 22000.00 Dr PDF002',
            '14/06/2026 AMAZON REFUND 799.00 Cr PDF003',
        ],
    )

    bank_rows = CSVParser().parse(str(bank), 'Bank Statement')
    pdf_rows = PDFParser().parse(str(pdf_path), 'Credit Card Statement PDF')

    assert classify_flags(bank_rows[0].description_raw, bank_rows[0].direction, bank_rows[0].amount)['is_transfer']
    assert clean_merchant(bank_rows[1].description_raw) == 'Airtel'
    assert classify_flags(bank_rows[2].description_raw, bank_rows[2].direction, bank_rows[2].amount)['is_refund']
    assert clean_merchant(pdf_rows[0].description_raw) == 'Zepto'
    assert classify_flags(pdf_rows[1].description_raw, pdf_rows[1].direction, pdf_rows[1].amount)['is_credit_card_payment']
    assert classify_flags(pdf_rows[2].description_raw, pdf_rows[2].direction, pdf_rows[2].amount)['is_refund']
