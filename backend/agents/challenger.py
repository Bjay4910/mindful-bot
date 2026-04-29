import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None

SYSTEM_PROMPT = """You are a recall challenge generator for a learning app.
Given a conversation, generate a focused recall question to test the user's memory and understanding.

You MUST return ONLY valid JSON — no markdown, no explanation, just the JSON object.
Format:
{
  "question": "A specific, testable recall question based on the conversation",
  "hint": "A subtle hint that guides without giving away the answer",
  "correct_answer": "The concise correct answer",
  "topic": "The main topic being tested"
}

Guidelines:
- Questions should test specific facts, concepts, or reasoning from the conversation
- Avoid yes/no questions — ask for explanations, definitions, or examples
- Keep the question clear and unambiguous"""


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    return _client


def generate_challenge(history: list[dict]) -> dict:
    """
    Generate a recall challenge based on conversation history.
    Returns dict with: question, hint, correct_answer, topic
    """
    client = _get_client()

    conversation_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" for msg in history[-10:]
    )
    prompt = f"Generate a recall challenge based on this conversation:\n\n{conversation_text}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)
