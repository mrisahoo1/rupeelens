def test_integrations_are_future_ready_and_do_not_claim_live_payments(client, main_headers):
    res = client.get('/api/integrations', headers=main_headers)
    assert res.status_code == 200
    data = res.json()
    by_id = {item['id']: item for item in data}

    assert {'account_aggregator_sync', 'bbps_bill_reminders', 'upi_export_import', 'email_statement_import', 'recurring_bill_detection'} <= set(by_id)
    assert by_id['upi_export_import']['status'] == 'current'
    assert by_id['upi_export_import']['live'] is True

    for key in ['account_aggregator_sync', 'bbps_bill_reminders', 'email_statement_import', 'recurring_bill_detection']:
        item = by_id[key]
        assert item['status'] == 'coming_soon'
        assert item['live'] is False
        assert item['data_flow']
        assert item['safeguards']
        assert item['endpoints']
        assert item['next_steps']

    assert 'No payment execution' in by_id['bbps_bill_reminders']['safeguards']
