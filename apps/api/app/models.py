from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default='user')
    account_type: Mapped[str] = mapped_column(String(40), default='main')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str] = mapped_column(String(160))
    bank: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last4: Mapped[str | None] = mapped_column(String(8), nullable=True)
    type: Mapped[str] = mapped_column(String(40), default='manual')
    billing_cycle_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billing_cycle_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_date: Mapped[int | None] = mapped_column(Integer, nullable=True)
    color: Mapped[str] = mapped_column(String(40), default='#7c3aed')
    icon: Mapped[str] = mapped_column(String(40), default='credit-card')

class ImportBatch(Base):
    __tablename__ = 'import_batches'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    source_type: Mapped[str] = mapped_column(String(80))
    source_file_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40), default='preview')
    parsed_rows: Mapped[list] = mapped_column(JSON, default=list)
    errors: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = (UniqueConstraint('user_id', 'dedupe_hash', name='uq_user_dedupe_hash'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    import_batch_id: Mapped[int | None] = mapped_column(ForeignKey('import_batches.id'), nullable=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    source_type: Mapped[str] = mapped_column(String(80), default='manual')
    source_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    posting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description_raw: Mapped[str] = mapped_column(Text)
    merchant_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    merchant_normalized: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(20), default='debit')
    currency: Mapped[str] = mapped_column(String(8), default='INR')
    category: Mapped[str] = mapped_column(String(120), default='Uncategorized')
    subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payment_mode: Mapped[str] = mapped_column(String(40), default='manual')
    card_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    card_last4: Mapped[str | None] = mapped_column(String(8), nullable=True)
    upi_app: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dedupe_hash: Mapped[str] = mapped_column(String(80), index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    is_refund: Mapped[bool] = mapped_column(Boolean, default=False)
    is_transfer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_credit_card_payment: Mapped[bool] = mapped_column(Boolean, default=False)
    is_excluded_from_spend: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    category_source: Mapped[str] = mapped_column(String(40), default='fallback')
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    revisit_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MerchantRule(Base):
    __tablename__ = 'merchant_rules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    pattern: Mapped[str] = mapped_column(String(255), index=True)
    merchant_normalized: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(120))
    subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)
    created_from_user_correction: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Budget(Base):
    __tablename__ = 'budgets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    month: Mapped[str] = mapped_column(String(7), index=True)
    category: Mapped[str] = mapped_column(String(120), default='Overall')
    amount: Mapped[float] = mapped_column(Float)

class Insight(Base):
    __tablename__ = 'insights'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    month: Mapped[str] = mapped_column(String(7), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(40), default='info')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
