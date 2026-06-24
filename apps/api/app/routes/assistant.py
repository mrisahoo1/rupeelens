from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import AssistantQuery
from ..services.assistant import answer_spend_question

router = APIRouter(prefix='/assistant', tags=['assistant'])

@router.post('/query')
def query_assistant(payload: AssistantQuery, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return answer_spend_question(db, user.id, payload.month, payload.question)
