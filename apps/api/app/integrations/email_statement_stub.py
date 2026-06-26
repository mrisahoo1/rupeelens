from .contracts import coming_soon_capability


class EmailStatementImportStub:
    live = False

    def capability(self):
        return coming_soon_capability(
            id='email_statement_import',
            name='Email statement auto-import',
            provider='Future mailbox connector',
            description='Future opt-in mailbox watcher for statement attachments. MVP does not read email, request mailbox scopes, or store mailbox tokens.',
            data_flow=['User connects mailbox', 'Find statement attachments by trusted sender rules', 'Store file in private storage', 'Run parser preview', 'Require user confirmation before import'],
            safeguards=['Opt-in only', 'No mailbox access in MVP', 'Attachment preview before import', 'Sender allowlist required before live launch'],
            endpoints=['GET /api/integrations', 'future: POST /api/integrations/email/connect', 'future: POST /api/integrations/email/import-preview'],
            next_steps=['Define mailbox OAuth scopes', 'Add sender allowlist rules', 'Add encrypted token storage', 'Route attachments through upload preview batches'],
        )

    def scan_mailbox(self, user_id: int):
        return {'status': 'coming_soon', 'live': False, 'provider': 'Email connector', 'attachments': [], 'user_id': user_id}
