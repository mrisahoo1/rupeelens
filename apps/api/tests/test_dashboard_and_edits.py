def test_dashboard_excludes_card_payments(client, demo_headers):
    data = client.get('/api/dashboard/summary?month=2026-06', headers=demo_headers).json()
    assert data['excluded_transfers'] >= 93000
    assert data['total_spend'] < data['excluded_transfers']
    assert data['upi_spend'] > 0

def test_transaction_edit_creates_user_rule(client, demo_headers):
    txs = client.get('/api/transactions?merchant=Local Cafe', headers=demo_headers).json()
    target = txs[0]['id']
    res = client.patch(f'/api/transactions/{target}', headers=demo_headers, json={'category':'Food & Dining','remark':'Worth reviewing','revisit_flag':True})
    assert res.status_code == 200
    rules = client.get('/api/rules', headers=demo_headers).json()
    assert any(r['created_from_user_correction'] and r['category'] == 'Food & Dining' for r in rules)
