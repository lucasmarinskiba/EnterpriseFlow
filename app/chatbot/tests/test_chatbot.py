# tests/test_chatbot.py
def test_automation_intent(client, auth_header):
    response = client.post('/chatbot/api/query', 
        json={"message": "Cómo crear un flujo automático?"},
        headers=auth_header
    )
    assert "flujos automatizados" in response.json['reply']
