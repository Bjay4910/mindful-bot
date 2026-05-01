class TestScores:
    def test_get_scores_requires_auth(self, client, test_user, auth_headers):
        login = client.post("/api/users/login", json={
            "email": test_user["email"],
            "password": test_user["password"],
        })
        user_id = login.get_json()["user"]["id"]

        resp = client.get(f"/api/scores/{user_id}")
        assert resp.status_code == 401

    def test_get_scores_success(self, client, test_user, auth_headers):
        login = client.post("/api/users/login", json={
            "email": test_user["email"],
            "password": test_user["password"],
        })
        user_id = login.get_json()["user"]["id"]

        resp = client.get(f"/api/scores/{user_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_points" in data
        assert "streak" in data
        assert isinstance(data["total_points"], int)
        assert isinstance(data["streak"], int)

    def test_get_scores_invalid_user(self, client, auth_headers):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.get(f"/api/scores/{fake_id}", headers=auth_headers)
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            data = resp.get_json()
            assert data["total_points"] == 0
            assert data["streak"] == 0


class TestLeaderboard:
    def test_leaderboard_public(self, client):
        resp = client.get("/api/leaderboard")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)

    def test_leaderboard_structure(self, client):
        resp = client.get("/api/leaderboard")
        data = resp.get_json()
        for entry in data["leaderboard"]:
            assert "username" in entry
            assert "total_points" in entry
            assert "rank" in entry
