import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.database import Base, engine, SessionLocal
from app.seed import ensure_users

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    ensure_users(db)
    print('Seeded RupeeLens users and demo data')
finally:
    db.close()
