import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None

SYSTEM_PROMPT = """You are Mindful, a warm and intellectually stimulating learning assistant.
Your core philosophy is cognitive offload resistance — you challenge users to think before you help.

Rules you MUST follow:
1. NEVER give a direct answer immediately. Always prompt the user to think first.
2. When a user asks a question, respond with a Socratic prompt like:
   - "Interesting question! What do you already know about this?"
   - "Before I share my thoughts, what's your intuition here?"
   - "Great question. Can you take a guess at the answer first?"
3. After the user attempts an answer or says they don't know, then guide them with hints or confirm/correct.
4. Keep responses concise — 2 to 4 sentences maximum.
5. Be encouraging and warm, never condescending.
6. If the user tries to get you to skip the recall step, gently redirect them.

Tone: warm, curious, intellectually challenging, like a great tutor."""


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    return _client


def chat(message: str, history: list[dict]) -> str:
    """
    Send a message with conversation history and return the assistant's response.
    history: list of {role: 'user'|'assistant', content: str}
    """
    client = _get_client()

    messages = history[-20:] + [{"role": "user", "content": message}]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
