from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .seed import ensure_users
from .routes import auth, accounts, uploads, transactions, dashboard, insights, budgets, rules, reports, integrations

app = FastAPI(title='RupeeLens API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(auth.router, prefix='/api')
app.include_router(accounts.router, prefix='/api')
app.include_router(uploads.router, prefix='/api')
app.include_router(transactions.router, prefix='/api')
app.include_router(dashboard.router, prefix='/api')
app.include_router(insights.router, prefix='/api')
app.include_router(budgets.router, prefix='/api')
app.include_router(rules.router, prefix='/api')
app.include_router(reports.router, prefix='/api')
app.include_router(integrations.router, prefix='/api')

@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try: ensure_users(db)
    finally: db.close()

@app.get('/api/health')
def health(): return {'ok': True, 'service': 'rupeelens'}
