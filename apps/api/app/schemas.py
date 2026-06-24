from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class LoginRequest(BaseModel): username: str; password: str
class TokenResponse(BaseModel): access_token: str; token_type: str = 'bearer'; user: dict
class AccountIn(BaseModel): name: str; bank: str | None = None; last4: str | None = None; type: str = 'manual'; billing_cycle_start: int | None = None; billing_cycle_end: int | None = None; due_date: int | None = None; color: str = '#7c3aed'; icon: str = 'credit-card'
class BudgetIn(BaseModel): month: str; category: str = 'Overall'; amount: float
class RuleIn(BaseModel): pattern: str; merchant_normalized: str; category: str; subcategory: str | None = None; priority: int = 20
class TransactionPatch(BaseModel): category: str | None = None; subcategory: str | None = None; remark: str | None = None; revisit_flag: bool | None = None; tags: list[str] | None = None
class ManualTransaction(BaseModel): transaction_date: date; description_raw: str; amount: float; direction: str = 'debit'; payment_mode: str = 'manual'; category: str | None = None; remark: str | None = None; revisit_flag: bool = False
class BulkUpdate(BaseModel): ids: list[int]; category: str | None = None; tags: list[str] | None = None; revisit_flag: bool | None = None
class ORMModel(BaseModel): model_config = ConfigDict(from_attributes=True)

class AssistantQuery(BaseModel):
    month: str
    question: str
