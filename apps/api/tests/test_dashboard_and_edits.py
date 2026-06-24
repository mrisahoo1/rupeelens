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

def test_csv_upload_preview_and_confirm_for_main_user(client, main_headers):
    csv = 'date,description,amount\n2026-06-25,UPI/ZOMATO/ORDER 123,321\n2026-06-26,CRED CC PAYMENT,12000\n'
    preview = client.post('/api/uploads', headers=main_headers, data={'source_type':'UPI CSV/XLSX'}, files=[('files', ('sample.csv', csv.encode(), 'text/csv'))])
    assert preview.status_code == 200
    batch = preview.json()[0]
    assert batch['parsed_rows'][0]['transaction_date'] == '2026-06-25'
    confirm = client.post(f'/api/uploads/{batch["id"]}/confirm', headers=main_headers)
    assert confirm.status_code == 200
    assert confirm.json()['inserted'] == 2
    summary = client.get('/api/dashboard/summary?month=2026-06', headers=main_headers).json()
    assert summary['total_spend'] == 321
    assert summary['excluded_transfers'] == 12000
