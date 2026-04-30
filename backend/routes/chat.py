from flask import Blueprint, request, jsonify
from backend.database.supabase import get_authed_client, get_user_from_token
from backend.agents import chatbot, challenger
from backend.limiter import limiter

chat_bp = Blueprint("chat", __name__)

CHALLENGE_EVERY = 3  # trigger challenge every N exchanges


def _require_auth():
    """Extract and verify Bearer token. Returns (user, token, error_response)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, None, (jsonify({"error": "Unauthorized"}), 401)
    token = auth[7:]
    user = get_user_from_token(token)
    if not user:
        return None, None, (jsonify({"error": "Invalid token"}), 401)
    return user, token, None


def _get_session_history(session_id: str, token: str) -> list[dict]:
    """Fetch last 20 messages for a session from Supabase."""
    try:
        db = get_authed_client(token)
        result = (
            db.table("messages")
            .select("role, content")
            .eq("session_id", session_id)
            .order("created_at")
            .limit(20)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[ERROR] _get_session_history failed: {e}")
        return []


@chat_bp.post("/chat")
@limiter.limit("30 per hour")
def send_message():
    user, token, err = _require_auth()
    if err:
        return err

    body = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    session_id = body.get("session_id", "").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    db = get_authed_client(token)

    # Ensure session exists
    try:
        db.table("sessions").upsert(
            {"id": session_id, "user_id": user.id}, on_conflict="id"
        ).execute()
    except Exception as e:
        print(f"[ERROR] sessions.upsert failed: {e}")

    # Fetch history before saving — used for AI context and exchange counting
    history = _get_session_history(session_id, token)

    # Get chatbot response
    try:
        response_text = chatbot.chat(message, history)
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500

    # Save user message and assistant response
    try:
        db.table("messages").insert([
            {"session_id": session_id, "role": "user", "content": message},
            {"session_id": session_id, "role": "assistant", "content": response_text},
        ]).execute()
        print(f"[INFO] messages saved for session {session_id}")
    except Exception as e:
        print(f"[ERROR] messages.insert failed: {e}")

    # Count user messages from history (+1 for the current message just sent).
    # Using history avoids a separate DB query and is immune to count query failures.
    prior_user_msgs = sum(1 for m in history if m["role"] == "user")
    exchange_count = prior_user_msgs + 1
    should_challenge = (exchange_count % CHALLENGE_EVERY == 0)

    print(f"[DEBUG] history_len={len(history)} prior_user_msgs={prior_user_msgs} exchange_count={exchange_count} CHALLENGE_EVERY={CHALLENGE_EVERY} should_challenge={should_challenge}")

    return jsonify({
        "response": response_text,
        "should_challenge": should_challenge,
        "exchange_count": exchange_count,
    })


@chat_bp.get("/chat/history")
def get_history():
    _, token, err = _require_auth()
    if err:
        return err

    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    history = _get_session_history(session_id, token)
    return jsonify({"messages": history})


@chat_bp.post("/challenge")
@limiter.limit("20 per hour")
def generate_challenge():
    _, token, err = _require_auth()
    if err:
        return err

    body = request.get_json(silent=True) or {}
    session_id = body.get("session_id", "").strip()
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    history = _get_session_history(session_id, token)
    if len(history) < 2:
        return jsonify({"error": "Not enough conversation to generate a challenge"}), 400

    try:
        challenge = challenger.generate_challenge(history)
    except Exception as e:
        return jsonify({"error": f"Challenge generation failed: {str(e)}"}), 500

    # Save challenge to DB (answer filled in after evaluation)
    try:
        db = get_authed_client(token)
        result = (
            db.table("challenges")
            .insert({
                "session_id": session_id,
                "question": challenge["question"],
                "correct_answer": challenge["correct_answer"],
            })
            .execute()
        )
        challenge["challenge_id"] = result.data[0]["id"] if result.data else None
    except Exception:
        challenge["challenge_id"] = None

    return jsonify(challenge)


@chat_bp.post("/challenge/evaluate")
@limiter.limit("20 per hour")
def evaluate_challenge():
    user, token, err = _require_auth()
    if err:
        return err

    body = request.get_json(silent=True) or {}
    challenge_id = body.get("challenge_id")
    question = (body.get("question") or "").strip()
    correct_answer = (body.get("correct_answer") or "").strip()
    user_answer = (body.get("user_answer") or "").strip()

    if not question or not user_answer:
        return jsonify({"error": "question and user_answer are required"}), 400

    from backend.agents import evaluator
    try:
        result = evaluator.evaluate(question, correct_answer, user_answer)
    except Exception as e:
        return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500

    score = result.get("score", 0)
    points_earned = score  # 1 point per score point

    # Update challenge record
    if challenge_id:
        try:
            db = get_authed_client(token)
            db.table("challenges").update({
                "user_answer": user_answer,
                "correct": result.get("is_correct", False),
                "score": score,
            }).eq("id", challenge_id).execute()
        except Exception:
            pass

    # Update user score via upsert
    try:
        db = get_authed_client(token)
        existing = db.table("scores").select("*").eq("user_id", user.id).execute()
        if existing.data:
            current = existing.data[0]
            new_total = current["total_points"] + points_earned
            new_streak = current["streak"] + 1
            new_longest = max(current.get("longest_streak", 0), new_streak)
            new_challenges = current.get("challenges_completed", 0) + 1
        else:
            new_total = points_earned
            new_streak = 1
            new_longest = 1
            new_challenges = 1

        db.table("scores").upsert({
            "user_id": user.id,
            "total_points": new_total,
            "streak": new_streak,
            "longest_streak": new_longest,
            "challenges_completed": new_challenges,
            "updated_at": "now()",
        }, on_conflict="user_id").execute()
        print(f"[INFO] score updated: user={user.id} total={new_total} streak={new_streak} longest={new_longest} challenges={new_challenges}")
    except Exception as e:
        print(f"[ERROR] score upsert failed: {e}")

    result["points_earned"] = points_earned
    return jsonify(result)
