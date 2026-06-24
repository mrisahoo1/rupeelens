def test_spend_assistant_answers_budget_question(client, demo_headers):
    res = client.post('/api/assistant/query', headers=demo_headers, json={'month':'2026-06','question':'How is my budget doing?'})
    assert res.status_code == 200
    body = res.json()
    assert body['mode'] in {'deterministic', 'ollama'}
    assert body['answer']
    assert body['cards']
    assert body['context']['month'] == '2026-06'
