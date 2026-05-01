from flask import Blueprint, request, jsonify
from backend.database.supabase import get_client, get_authed_client, get_service_client, get_user_from_token

users_bp = Blueprint("users", __name__)


def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, None, (jsonify({"error": "Unauthorized"}), 401)
    token = auth[7:]
    user = get_user_from_token(token)
    if not user:
        return None, None, (jsonify({"error": "Invalid token"}), 401)
    return user, token, None


@users_bp.post("/users/register")
def register():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip()
    password = (body.get("password") or "").strip()
    username = (body.get("username") or "").strip()

    if not email or not password or not username:
        return jsonify({"error": "email, password, and username are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_client()
    try:
        auth_response = db.auth.sign_up({"email": email, "password": password})
        if not auth_response.user:
            return jsonify({"error": "Registration failed"}), 400

        user_id = auth_response.user.id

        service_db = get_service_client()

        # Create user profile
        service_db.table("users").insert({
            "id": user_id,
            "username": username,
            "email": email,
        }).execute()

        # Initialize score
        service_db.table("scores").insert({
            "user_id": user_id,
            "total_points": 0,
            "streak": 0,
        }).execute()

        session_data = None
        if auth_response.session:
            session_data = {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
            }

        return jsonify({
            "user": {"id": user_id, "email": email, "username": username},
            "session": session_data,
            "message": "Registration successful. Check your email to confirm your account.",
        })
    except Exception as e:
        err_str = str(e)
        if "users_email_key" in err_str:
            return jsonify({"error": "An account with this email already exists"}), 400
        if "users_username_key" in err_str:
            return jsonify({"error": "This username is already taken"}), 400
        return jsonify({"error": "Registration failed. Please try again."}), 400


@users_bp.post("/users/login")
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip()
    password = (body.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    db = get_client()
    try:
        auth_response = db.auth.sign_in_with_password({"email": email, "password": password})
        if not auth_response.user or not auth_response.session:
            return jsonify({"error": "Invalid credentials"}), 401

        user = auth_response.user
        profile = db.table("users").select("username").eq("id", user.id).execute()
        username = profile.data[0]["username"] if profile.data else user.email

        return jsonify({
            "user": {"id": user.id, "email": user.email, "username": username},
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
            },
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@users_bp.get("/users/<user_id>")
def get_user(user_id):
    user, token, err = _require_auth()
    if err:
        return err

    db = get_authed_client(token)
    try:
        result = db.table("users").select("id, username, email, created_at").eq("id", user_id).execute()
        if not result.data:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user": result.data[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.delete("/users/<user_id>")
def delete_user(user_id):
    user, token, err = _require_auth()
    if err:
        return err
    if user.id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    try:
        service_db = get_service_client()
        service_db.table("users").delete().eq("id", user_id).execute()
        service_db.auth.admin.delete_user(user_id)
        return jsonify({"message": "Account deleted successfully"})
    except Exception as e:
        print(f"[ERROR] delete_user failed: {e}")
        return jsonify({"error": "Could not delete account. Please try again."}), 500
