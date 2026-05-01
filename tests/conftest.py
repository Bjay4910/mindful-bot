import pytest
import uuid
from backend.app import app
from backend.database.supabase import get_service_client

# Unique credentials per test run to avoid conflicts
_uid = uuid.uuid4().hex[:8]
_TEST_USER = {
    "username": f"testuser_{_uid}",
    "email": f"test_{_uid}@mindful-test.com",
    "password": "TestPassword123!",
}


@pytest.fixture(scope="session")
def client():
    app.config["TESTING"] = True
    app.config["RATELIMIT_ENABLED"] = False  # disable rate limiting in tests
    with app.test_client() as c:
        yield c


@pytest.fixture(scope="session")
def test_user():
    return _TEST_USER.copy()


@pytest.fixture(scope="session")
def auth_headers(client, test_user):
    # Register test user
    reg = client.post("/api/users/register", json=test_user)
    reg_data = reg.get_json()
    assert reg.status_code == 200, f"Registration failed: {reg_data}"

    # Login to get token
    login = client.post("/api/users/login", json={
        "email": test_user["email"],
        "password": test_user["password"],
    })
    login_data = login.get_json()
    assert login.status_code == 200, f"Login failed: {login_data}"

    user_id = login_data["user"]["id"]
    token = login_data["session"]["access_token"]

    yield {"Authorization": f"Bearer {token}"}

    # Cleanup: delete test user from all tables after session ends
    try:
        db = get_service_client()
        db.table("scores").delete().eq("user_id", user_id).execute()
        db.table("users").delete().eq("id", user_id).execute()
        db.auth.admin.delete_user(user_id)
    except Exception as e:
        print(f"[TEST CLEANUP] Failed to delete test user {user_id}: {e}")
