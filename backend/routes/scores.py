from flask import Blueprint, request, jsonify
from backend.database.supabase import get_client, get_user_from_token

scores_bp = Blueprint("scores", __name__)


def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    token = auth[7:]
    user = get_user_from_token(token)
    if not user:
        return None, (jsonify({"error": "Invalid token"}), 401)
    return user, None


@scores_bp.get("/scores/<user_id>")
def get_score(user_id):
    user, err = _require_auth()
    if err:
        return err

    db = get_client()
    try:
        result = db.table("scores").select("*").eq("user_id", user_id).execute()
        if not result.data:
            return jsonify({"total_points": 0, "streak": 0})

        score = result.data[0]

        # Get rank: fetch full leaderboard and find position by total_points
        rank = None
        try:
            lb = db.table("leaderboard").select("*").execute()
            if lb.data:
                user_points = score["total_points"]
                # rank = position among entries with >= total_points
                rank = sum(1 for row in lb.data if row.get("total_points", 0) >= user_points)
                if rank == 0:
                    rank = len(lb.data)
        except Exception as e:
            print(f"[ERROR] leaderboard rank lookup failed: {e}")

        return jsonify({
            "total_points": score["total_points"],
            "streak": score["streak"],
            "rank": rank,
        })
    except Exception as e:
        print(f"[ERROR] get_score failed: {e}")
        return jsonify({"error": str(e)}), 500


@scores_bp.get("/leaderboard")
def get_leaderboard():
    db = get_client()
    try:
        result = db.table("leaderboard").select("*").limit(20).execute()
        return jsonify({"leaderboard": result.data or []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
