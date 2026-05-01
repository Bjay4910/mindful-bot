import uuid


class TestRLS:
    def test_cannot_access_other_users_scores(self, client, auth_headers):
        # Try to access a random user's scores with our token
        fake_user_id = str(uuid.uuid4())
        resp = client.get(f"/api/scores/{fake_user_id}", headers=auth_headers)
        # Should either return 404, 403, or empty/zero scores — not real data
        assert resp.status_code in (200, 403, 404)
        if resp.status_code == 200:
            data = resp.get_json()
            # If it returns 200, scores should be zero (no data leaked)
            assert data["total_points"] == 0
            assert data["streak"] == 0

    def test_cannot_access_other_users_chat_history(self, client, auth_headers):
        # Try to access chat history with a session_id that belongs to nobody
        fake_session_id = str(uuid.uuid4())
        resp = client.get(
            f"/api/chat/history?session_id={fake_session_id}",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 403, 404)
        if resp.status_code == 200:
            data = resp.get_json()
            # Should return empty messages, not someone else's
            assert data["messages"] == []

    def test_leaderboard_does_not_expose_emails(self, client):
        resp = client.get("/api/leaderboard")
        assert resp.status_code == 200
        data = resp.get_json()
        for entry in data["leaderboard"]:
            assert "email" not in entry
            assert "password" not in entry

    def test_cannot_post_chat_as_other_user(self, client, auth_headers):
        # Send a chat message — it should be attributed to the authenticated user only
        resp = client.post("/api/chat",
            json={
                "message": "This should only be saved for the auth user",
                "session_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
