import uuid

# Shared session ID across tests that need history to accumulate
SESSION_ID = str(uuid.uuid4())


class TestChatEndpoint:
    def test_chat_requires_auth(self, client):
        resp = client.post("/api/chat", json={
            "message": "Hello",
            "session_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 401
        assert "error" in resp.get_json()

    def test_chat_missing_message(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={"session_id": str(uuid.uuid4())},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_chat_returns_response(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={"message": "What is photosynthesis?", "session_id": SESSION_ID},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert "exchange_count" in data
        assert "should_challenge" in data

    def test_new_session_created(self, client, auth_headers):
        # Verify the session from the previous test has messages saved
        resp = client.get(
            f"/api/chat/history?session_id={SESSION_ID}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "messages" in data
        assert len(data["messages"]) > 0

    def test_chat_history(self, client, auth_headers):
        resp = client.get(
            f"/api/chat/history?session_id={SESSION_ID}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        # Each message should have role and content
        for msg in data["messages"]:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ("user", "assistant")
