from app.database import Base, engine, SessionLocal
from app.seed import ensure_users
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    ensure_users(db)
    print('Seeded RupeeLens users and demo data')
finally:
    db.close()
