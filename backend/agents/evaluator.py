import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None

SYSTEM_PROMPT = """You are an answer evaluator for a learning application.
Score the user's answer to a recall question on a scale of 0 to 10.

You MUST return ONLY valid JSON — no markdown, no explanation, just the JSON object.
Format:
{
  "score": 8,
  "feedback": "Specific, encouraging feedback on their answer",
  "correct_answer": "The correct answer in full",
  "is_correct": true
}

Scoring guide:
- 0-2: No attempt or completely wrong
- 3-4: Has the right idea but mostly incorrect
- 5-6: Partially correct, missing key details
- 7-8: Mostly correct with minor gaps
- 9-10: Accurate and complete

Rules:
- Be neither too strict nor too generous
- Feedback must be specific and constructive — mention what they got right AND what was missing
- is_correct = true only if score >= 7
- Keep feedback to 1-2 sentences"""


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    return _client


def evaluate(question: str, correct_answer: str, user_answer: str) -> dict:
    """
    Evaluate a user's recall answer.
    Returns dict with: score, feedback, correct_answer, is_correct
    """
    client = _get_client()

    prompt = (
        f"Question: {question}\n"
        f"Correct answer: {correct_answer}\n"
        f"User's answer: {user_answer}\n\n"
        "Evaluate the user's answer."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)
