from .contracts import coming_soon_capability


class AccountAggregatorStub:
    live = False

    def capability(self):
        return coming_soon_capability(
            id='account_aggregator_sync',
            name='Account Aggregator consent sync',
            provider='RBI Account Aggregator ecosystem',
            description='Consent-based bank and credit account transaction sync placeholder. No consent handle is created and no FIU/FIP call is made in MVP.',
            data_flow=['Create consent request', 'User approves with AA app', 'Fetch encrypted financial information', 'Normalize transactions', 'Revoke or expire consent'],
            safeguards=['Explicit consent required', 'No credential sharing', 'User-owned records only', 'Consent expiry and revocation required before live launch'],
            endpoints=['GET /api/integrations', 'future: POST /api/integrations/account-aggregator/consents', 'future: POST /api/integrations/account-aggregator/sync'],
            next_steps=['Select licensed AA/FIU partner', 'Add consent ledger table', 'Encrypt consent artifacts', 'Map AA transaction schema into parser pipeline'],
        )

    def sync_transactions(self, user_id: int):
        return {'status': 'coming_soon', 'live': False, 'provider': 'Account Aggregator', 'transactions': [], 'user_id': user_id}
