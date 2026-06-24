def test_demo_login_returns_demo_user(client):
    res = client.post('/api/auth/login', json={'username':'demo','password':'demo123'})
    assert res.status_code == 200
    assert res.json()['user']['account_type'] == 'demo'

def test_main_user_starts_empty_and_demo_has_seed_data(client, demo_headers, main_headers):
    demo = client.get('/api/transactions', headers=demo_headers)
    main = client.get('/api/transactions', headers=main_headers)
    assert demo.status_code == 200 and len(demo.json()) > 10
    assert main.status_code == 200 and main.json() == []

def test_demo_upload_is_disabled(client, demo_headers):
    res = client.post('/api/uploads', headers=demo_headers, data={'source_type':'UPI CSV/XLSX'}, files=[('files', ('x.csv', b'date,description,amount\n2026-06-01,Zomato,100', 'text/csv'))])
    assert res.status_code == 403
