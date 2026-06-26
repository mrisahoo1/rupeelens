from .contracts import coming_soon_capability


class SetuBillPayStub:
    live = False

    def capability(self):
        return coming_soon_capability(
            id='bbps_bill_reminders',
            name='Bharat Connect / BBPS bill reminders',
            provider='Bharat Connect / BBPS via future provider adapter',
            description='Future utility bill fetch and reminder module. MVP does not fetch live bills, initiate payments, or claim BBPS connectivity.',
            data_flow=['Store biller metadata', 'Fetch bill due details after user authorization', 'Create reminder events', 'Match paid bills from transactions', 'Never execute payment in MVP'],
            safeguards=['Coming soon only', 'No payment execution', 'No saved payment instrument', 'Reminder-only UI until live compliance review'],
            endpoints=['GET /api/integrations', 'future: GET /api/integrations/bbps/billers', 'future: POST /api/integrations/bbps/reminders'],
            next_steps=['Choose BBPS provider', 'Add biller and reminder tables', 'Build due-date notification worker', 'Add paid-bill reconciliation rules'],
        )

    def upcoming_bills(self, user_id: int):
        return {'status': 'coming_soon', 'live': False, 'provider': 'Bharat Connect / BBPS', 'bills': [], 'user_id': user_id}
