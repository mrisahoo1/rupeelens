from datetime import date
from sqlalchemy.orm import Session
from .config import get_settings
from .models import User, Account, Transaction, Budget
from .security import hash_password, verify_password
from .services.rules import seed_global_rules, categorize
from .services.normalization import classify_flags, dedupe_hash

DEMO_ROWS = [
    ('2026-06-01','UPI/ZOMATO/ORDER 8871',640,'debit','upi'),('2026-06-02','SWIGGY PAYMENTS',520,'debit','upi'),('2026-06-03','AMZN Mktp IN',2499,'debit','credit_card'),('2026-06-04','NETFLIX MUMBAI',649,'debit','credit_card'),('2026-06-05','SPOTIFY INDIA',119,'debit','credit_card'),('2026-06-06','UBER TRIP HELP.UBER.COM',380,'debit','upi'),('2026-06-07','BLINKIT GROCERY',1240,'debit','upi'),('2026-06-08','CRED CC PAYMENT',48000,'debit','bank'),('2026-06-09','HDFC CREDIT CARD PAYMENT',35000,'debit','bank'),('2026-06-10','IRCTC UPI',2180,'debit','upi'),('2026-06-11','BOOKMYSHOW',960,'debit','credit_card'),('2026-06-12','AIRTEL BILL PAYMENT',999,'debit','upi'),('2026-06-13','APOLLO PHARMACY',730,'debit','credit_card'),('2026-06-14','SELF TRANSFER TO SBI',10000,'debit','bank'),('2026-06-15','AMAZON REFUND',799,'credit','credit_card'),('2026-06-16','ZEPTOPAY',870,'debit','upi'),('2026-06-17','OLA CABS',450,'debit','credit_card'),('2026-06-18','PRIME VIDEO',299,'debit','credit_card'),('2026-06-19','LOCAL CAFE BANDRA',820,'debit','manual'),('2026-06-20','FUEL PUMP HPCL',3200,'debit','credit_card'),('2026-06-21','MSEB ELECTRICITY',1870,'debit','upi'),('2026-06-22','MYNTRA DESIGNS',2199,'debit','credit_card'),('2026-06-23','RAPIDO BIKE',96,'debit','upi'),('2026-06-24','PAYU COURSE',3999,'debit','credit_card')
]

def _desired_hash(current_hash: str | None, plaintext: str | None, explicit_hash: str | None, fallback_password: str) -> str:
    if explicit_hash:
        return explicit_hash
    password = plaintext or fallback_password
    if current_hash and verify_password(password, current_hash):
        return current_hash
    return hash_password(password)

def ensure_users(db: Session):
    settings = get_settings()
    seed_global_rules(db)
    main = db.query(User).filter(User.username == settings.main_username).first()
    if not main:
        main = User(username=settings.main_username, password_hash=_desired_hash(None, settings.main_password, settings.main_password_hash, 'change-me-now'), role='owner', account_type='main')
        db.add(main)
    else:
        main.password_hash = _desired_hash(main.password_hash, settings.main_password, settings.main_password_hash, 'change-me-now')
        main.role = 'owner'
        main.account_type = 'main'
    demo = db.query(User).filter(User.username == settings.demo_username).first()
    if not demo:
        demo = User(username=settings.demo_username, password_hash=_desired_hash(None, settings.demo_password, settings.demo_password_hash, 'demo123'), role='demo', account_type='demo')
        db.add(demo)
        db.commit()
        seed_demo_data(db, demo)
    else:
        demo.password_hash = _desired_hash(demo.password_hash, settings.demo_password, settings.demo_password_hash, 'demo123')
        demo.role = 'demo'
        demo.account_type = 'demo'
    db.commit()
    seed_demo_data(db, demo)

def seed_demo_data(db: Session, user: User):
    if db.query(Transaction).filter(Transaction.user_id == user.id).first():
        return
    cards = [Account(user_id=user.id, name='HDFC Regalia', bank='HDFC', last4='1821', type='credit_card', color='#4f46e5'), Account(user_id=user.id, name='ICICI Amazon Pay', bank='ICICI', last4='9088', type='credit_card', color='#f59e0b'), Account(user_id=user.id, name='UPI Wallet', bank='UPI', type='upi', color='#14b8a6'), Account(user_id=user.id, name='SBI Salary', bank='SBI', type='bank', color='#38bdf8')]
    db.add_all(cards); db.commit()
    mode_account = {'credit_card': cards[0], 'upi': cards[2], 'bank': cards[3], 'manual': None}
    for raw_date, desc, amount, direction, mode in DEMO_ROWS:
        cat = categorize(db, user.id, desc); flags = classify_flags(desc, direction, amount); tx_date = date.fromisoformat(raw_date); account = mode_account[mode]
        db.add(Transaction(user_id=user.id, account_id=getattr(account, 'id', None), source_type='demo_seed', source_file_name='demo', transaction_date=tx_date, posting_date=tx_date, description_raw=desc, merchant_raw=desc, amount=amount, direction=direction, payment_mode=mode, card_name=getattr(account, 'name', None) if mode == 'credit_card' else None, card_last4=getattr(account, 'last4', None), dedupe_hash=dedupe_hash(user.id, tx_date, amount, cat['merchant_normalized'], None), remark='Review this discretionary spend' if 'CAFE' in desc else None, revisit_flag='CAFE' in desc or 'MYNTRA' in desc, tags=['demo'], **cat, **flags))
    db.add(Budget(user_id=user.id, month='2026-06', category='Overall', amount=65000))
    db.add(Budget(user_id=user.id, month='2026-06', category='Food & Dining', amount=9000))
    db.commit()
