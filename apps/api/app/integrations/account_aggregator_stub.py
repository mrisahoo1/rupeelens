class AccountAggregatorStub:
    live = False
    def sync_transactions(self, user_id: int):
        return {'status': 'coming_soon', 'provider': 'Account Aggregator', 'transactions': []}
