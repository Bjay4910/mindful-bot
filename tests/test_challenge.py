import uuid


class TestChallenge:
    def test_challenge_requires_auth(self, client):
        resp = client.post("/api/challenge", json={
            "session_id": str(uuid.uuid4()),
        })
        assert resp.status_code == 401

    def test_challenge_no_history(self, client, auth_headers):
        # Fresh session with no messages should return 400
        resp = client.post("/api/challenge",
            json={"session_id": str(uuid.uuid4())},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_challenge_missing_session_id(self, client, auth_headers):
        resp = client.post("/api/challenge",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()


class TestChallengeEvaluate:
    def test_evaluate_requires_auth(self, client):
        resp = client.post("/api/challenge/evaluate", json={
            "question": "What is photosynthesis?",
            "user_answer": "It is how plants make food",
        })
        assert resp.status_code == 401

    def test_evaluate_missing_fields(self, client, auth_headers):
        # Missing user_answer
        resp = client.post("/api/challenge/evaluate",
            json={"question": "What is photosynthesis?"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_evaluate_success(self, client, auth_headers):
        resp = client.post("/api/challenge/evaluate",
            json={
                "question": "What is photosynthesis?",
                "correct_answer": "The process by which plants convert sunlight into food",
                "user_answer": "Plants use sunlight to make food from CO2 and water",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "score" in data
        assert "feedback" in data
        assert "is_correct" in data
        assert "points_earned" in data
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 10
