import uuid


class TestInputValidation:
    def test_sql_injection_in_message(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={
                "message": "'; DROP TABLE users; --",
                "session_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )
        # Should handle gracefully, not crash
        assert resp.status_code in (200, 400)

    def test_oversized_message(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={
                "message": "A" * 100000,
                "session_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )
        # Should reject or handle gracefully
        assert resp.status_code in (200, 400, 413)

    def test_empty_message(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={
                "message": "",
                "session_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_invalid_session_id_format(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={
                "message": "Hello",
                "session_id": "not-a-valid-uuid",
            },
            headers=auth_headers,
        )
        assert resp.status_code in (200, 400)

    def test_xss_in_username(self, client):
        resp = client.post("/api/users/register", json={
            "username": "<script>alert('xss')</script>",
            "email": f"xss_{uuid.uuid4().hex[:6]}@test.com",
            "password": "Password123!",
        })
        # Should either reject or store as plain text (not execute)
        assert resp.status_code in (200, 400)

    def test_empty_body(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_null_values(self, client, auth_headers):
        resp = client.post("/api/chat",
            json={
                "message": None,
                "session_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
