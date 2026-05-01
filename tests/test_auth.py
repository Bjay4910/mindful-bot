class TestRegister:
    def test_register_missing_fields(self, client):
        resp = client.post("/api/users/register", json={
            "email": "nopass@mindful-test.com",
            "username": "nopasuser",
            # password missing
        })
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_register_duplicate_email(self, client, test_user, auth_headers):
        # auth_headers already registered test_user — same email should fail
        resp = client.post("/api/users/register", json={
            "email": test_user["email"],
            "password": "AnotherPass123!",
            "username": "different_username",
        })
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_register_duplicate_username(self, client, test_user, auth_headers):
        # username column has UNIQUE NOT NULL constraint (supabase_schema.sql line 6)
        resp = client.post("/api/users/register", json={
            "email": "unique_email@mindful-test.com",
            "password": "AnotherPass123!",
            "username": test_user["username"],
        })
        assert resp.status_code == 400
        assert "error" in resp.get_json()


class TestLogin:
    def test_login_success(self, client, test_user, auth_headers):
        resp = client.post("/api/users/login", json={
            "email": test_user["email"],
            "password": test_user["password"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "session" in data
        assert "access_token" in data["session"]
        assert "user" in data
        assert data["user"]["email"] == test_user["email"]

    def test_login_wrong_password(self, client, test_user, auth_headers):
        resp = client.post("/api/users/login", json={
            "email": test_user["email"],
            "password": "WrongPassword999!",
        })
        assert resp.status_code in (400, 401)
        assert "error" in resp.get_json()

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/users/login", json={
            "email": "doesnotexist@mindful-test.com",
            "password": "SomePassword123!",
        })
        assert resp.status_code in (400, 401)
        assert "error" in resp.get_json()
