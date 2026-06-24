class SetuBillPayStub:
    live = False
    def upcoming_bills(self, user_id: int):
        return {'status': 'coming_soon', 'provider': 'Bharat Connect / BBPS', 'bills': []}
