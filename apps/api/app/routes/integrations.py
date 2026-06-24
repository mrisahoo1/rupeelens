from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import User
router = APIRouter(prefix='/integrations', tags=['integrations'])
@router.get('')
def integrations(user: User = Depends(get_current_user)):
    return [{'name':'Bharat Connect / BBPS bill fetch and payment','status':'coming_soon'}, {'name':'Account Aggregator transaction sync','status':'coming_soon'}, {'name':'UPI app export import','status':'current'}, {'name':'Email statement auto-import','status':'coming_soon'}]
