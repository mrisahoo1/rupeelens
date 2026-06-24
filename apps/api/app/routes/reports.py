import csv, io
from fastapi import APIRouter, Depends, Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import Transaction, User
from ..services.analytics import summary
router = APIRouter(prefix='/reports', tags=['reports'])
@router.get('/monthly')
def monthly(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = summary(db, user.id, month); score = max(0, min(100, 82 - data['uncategorized'] * 2 - data['needs_revisit'] * 3)); return {**data, 'financial_awareness_score': score}
@router.get('/export.csv')
def export_csv(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if month: q = q.filter(Transaction.transaction_date >= f'{month}-01', Transaction.transaction_date < f'{month}-32')
    out = io.StringIO(); writer = csv.writer(out); writer.writerow(['date','merchant','amount','direction','category','mode','remark'])
    for t in q.all(): writer.writerow([t.transaction_date, t.merchant_normalized, t.amount, t.direction, t.category, t.payment_mode, t.remark or ''])
    return Response(out.getvalue(), media_type='text/csv', headers={'Content-Disposition':'attachment; filename=rupeelens.csv'})
@router.get('/export.pdf')
def export_pdf(month: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = summary(db, user.id, month); buf = io.BytesIO(); p = canvas.Canvas(buf, pagesize=A4); p.setTitle('RupeeLens Monthly Report'); p.drawString(72, 790, f'RupeeLens Monthly Report - {month}'); p.drawString(72, 760, f'Total Spend: INR {data["total_spend"]:,.2f}'); p.drawString(72, 740, f'Top Category: {data["top_category"]}'); p.drawString(72, 720, f'Top Merchant: {data["top_merchant"]}'); p.save(); return Response(buf.getvalue(), media_type='application/pdf')
