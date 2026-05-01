import uuid


class TestAuthBypass:
    def test_chat_no_token(self, client):
        resp = client.post("/api/chat", json={
            "message": "Hello",
            "session_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 401

    def test_chat_fake_token(self, client):
        resp = client.post("/api/chat",
            json={"message": "Hello", "session_id": str(uuid.uuid4())},
            headers={"Authorization": "Bearer faketoken123"},
        )
        assert resp.status_code == 401

    def test_chat_malformed_auth_header(self, client):
        resp = client.post("/api/chat",
            json={"message": "Hello", "session_id": str(uuid.uuid4())},
            headers={"Authorization": "NotBearer token"},
        )
        assert resp.status_code == 401

    def test_scores_no_token(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/scores/{fake_id}")
        assert resp.status_code == 401

    def test_challenge_no_token(self, client):
        resp = client.post("/api/challenge", json={
            "session_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 401

    def test_evaluate_no_token(self, client):
        resp = client.post("/api/challenge/evaluate", json={
            "question": "What is X?",
            "user_answer": "X is Y",
        })
        assert resp.status_code == 401
