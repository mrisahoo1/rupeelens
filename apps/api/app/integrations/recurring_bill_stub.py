from .contracts import coming_soon_capability


class RecurringBillDetectionStub:
    live = False

    def capability(self):
        return coming_soon_capability(
            id='recurring_bill_detection',
            name='Recurring bill detection',
            provider='RupeeLens deterministic rules',
            description='Future bill intelligence layer that promotes recurring utilities/subscriptions into reminders. Current insights detect subscriptions; this module is the reminder architecture boundary.',
            data_flow=['Cluster merchants by cadence', 'Detect due-date pattern', 'Ask user to confirm bill identity', 'Create reminder candidate', 'Reconcile against future transactions'],
            safeguards=['Deterministic and explainable', 'User confirmation before reminder creation', 'No payment action', 'False positives stay as suggestions'],
            endpoints=['GET /api/integrations', 'future: GET /api/integrations/recurring-bills/candidates', 'future: POST /api/integrations/recurring-bills/confirm'],
            next_steps=['Add bill_candidates table', 'Reuse insights recurring merchant evidence', 'Add reminder status workflow', 'Surface ignored/resolved candidates'],
        )

    def detect_candidates(self, user_id: int):
        return {'status': 'coming_soon', 'live': False, 'provider': 'RupeeLens rules', 'candidates': [], 'user_id': user_id}
