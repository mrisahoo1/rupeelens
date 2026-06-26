from fastapi import APIRouter, Depends
from ..deps import get_current_user
from ..models import User
from ..integrations.account_aggregator_stub import AccountAggregatorStub
from ..integrations.email_statement_stub import EmailStatementImportStub
from ..integrations.recurring_bill_stub import RecurringBillDetectionStub
from ..integrations.setu_billpay_stub import SetuBillPayStub

router = APIRouter(prefix='/integrations', tags=['integrations'])


def upi_export_capability():
    return {
        'id': 'upi_export_import',
        'name': 'UPI app export import',
        'status': 'current',
        'live': True,
        'provider': 'PhonePe / Google Pay / Paytm / BHIM exports',
        'description': 'Current manual export workflow. Users upload CSV/XLSX/PDF exports, review parsed rows, then confirm import.',
        'data_flow': ['Upload export', 'Parse and normalize', 'Review preview rows', 'Confirm import', 'Analyze spend'],
        'safeguards': ['User-owned upload batch', 'Preview before import', 'Duplicate detection', 'Transfers and card payments excluded from spend'],
        'endpoints': ['POST /api/uploads', 'GET /api/uploads', 'POST /api/uploads/{id}/confirm'],
        'next_steps': ['Keep expanding parser profiles', 'Improve column mapping UI', 'Add provider-specific parse reports'],
    }


@router.get('')
def integrations(user: User = Depends(get_current_user)):
    return [
        AccountAggregatorStub().capability().to_dict(),
        SetuBillPayStub().capability().to_dict(),
        upi_export_capability(),
        EmailStatementImportStub().capability().to_dict(),
        RecurringBillDetectionStub().capability().to_dict(),
    ]
