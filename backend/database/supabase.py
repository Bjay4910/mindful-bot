import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print(f"[ERROR] Supabase env vars missing — SUPABASE_URL={'set' if url else 'MISSING'}, SUPABASE_KEY={'set' if key else 'MISSING'}")
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _client = create_client(url, key)
        print(f"[INFO] Supabase client created for {url}")
    return _client


def get_authed_client(token: str) -> Client:
    """Return a per-request Supabase client with the user's JWT set.
    This makes auth.uid() work correctly in RLS policies."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    client = create_client(url, key)
    client.postgrest.auth(token)
    return client


def get_user_from_token(token: str):
    """Verify a Supabase JWT and return the user, or None if invalid."""
    try:
        client = get_client()
        response = client.auth.get_user(token)
        return response.user
    except Exception as e:
        print(f"[ERROR] get_user_from_token failed: {e}")
        return None
