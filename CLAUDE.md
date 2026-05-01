# mindful-bot — CLAUDE.md

## Project Overview
mindful-bot is a cognitive offload resistance chatbot. It challenges users to think
and recall before revealing answers. Built as a full-stack web application for an
Intelligent Systems course.

---

## Core Philosophy
- Never show answers immediately
- Always prompt user to think first
- Reward active recall with points
- Track progress honestly

---

## Live URLs
- Frontend: https://mindful-bot-three.vercel.app (Vercel)
- Backend API: https://mindful-bot.onrender.com (Render)
- Local frontend: http://localhost:5500 (Live Server)
- Local backend: http://localhost:5001

---

## Tech Stack
- Frontend: Plain HTML, CSS, Vanilla JavaScript
- Animations: AOS (Animate On Scroll) + CSS
- Backend: Python Flask + Gunicorn
- Database: Supabase (PostgreSQL)
- AI: Anthropic Claude API (claude-sonnet-4-6)
- Auth: Supabase Auth (email + password, JWT)
- Rate Limiting: flask-limiter (200/day, 50/hr global; 30/hr chat, 20/hr challenges)
- Testing: pytest

---

## What's Fully Working
- User registration and login (Supabase Auth + JWT)
- Socratic chatbot (Agent 1) — never answers directly, prompts recall first
- Recall challenge system (Agent 2) — triggers every 3 exchanges
- Challenge evaluator (Agent 3) — scores 0–10, gives feedback
- Points, streak, and longest_streak tracking after every evaluated challenge
- Global leaderboard (Supabase RANK() view, top 20)
- Progress dashboard (score, streak, rank, recent sessions)
- Session topic auto-detection on first message (lightweight Claude call)
- Settings page (update username, email, password, delete account)
- Auth guard on all protected pages
- CORS restricted to known frontend origins
- RLS enforced on all tables via per-request JWT (get_authed_client)
- Service role client (get_service_client) for registration inserts that bypass RLS
- Rate limiting on all AI routes
- Circular import resolved (limiter.py isolated from app.py)
- Dynamic API base URL (localhost vs production via window.location.hostname)
- Theme switcher (Light / Dark / Deep Space)
- 3D bubble canvas animation with depth background
- Profile dropdown with settings link

## What's Pending / Known Issues
- test suite is scaffolded but most test files are empty (only test_auth.py written)
- test_register_duplicate_username depends on UNIQUE constraint on users.username (confirmed in schema)
- Session topic detection adds ~1 extra Claude API call per new session
- No pagination on leaderboard (renders all users up to limit 20)
- No mobile-optimised chat keyboard handling
- Registration: if Supabase has email confirmation enabled, session is null and user is not auto-logged in after register

---

## Project Structure

```
mindful-bot/
├── frontend/
│   ├── index.html          # Landing page
│   ├── chat.html           # Chat interface
│   ├── dashboard.html      # User progress dashboard
│   ├── leaderboard.html    # Global rankings
│   ├── settings.html       # Account settings
│   ├── features.html       # Features page
│   ├── about.html          # About page
│   ├── privacy.html        # Privacy policy
│   ├── terms.html          # Terms of service
│   ├── contact.html        # Contact page
│   ├── css/
│   │   ├── main.css        # Design system + all components
│   │   └── notion.css      # Notion-inspired base styles
│   └── js/
│       ├── config.js       # Supabase + API config (dynamic base URL)
│       ├── main.js         # Shared auth, nav, toast, apiFetch
│       ├── chat.js         # Chat + challenge flow
│       ├── dashboard.js    # Dashboard data fetching
│       └── leaderboard.js  # Leaderboard rendering
├── backend/
│   ├── app.py              # Flask entry point, CORS, rate limiter init
│   ├── limiter.py          # Isolated Limiter instance (avoids circular import)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── chatbot.py      # Socratic chatbot (Agent 1)
│   │   ├── challenger.py   # Recall challenge generator (Agent 2)
│   │   └── evaluator.py    # Challenge evaluator + scorer (Agent 3)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py         # /api/chat, /api/challenge, /api/challenge/evaluate
│   │   ├── scores.py       # /api/scores, /api/leaderboard
│   │   └── users.py        # /api/users/register, login, profile
│   └── database/
│       ├── __init__.py
│       └── supabase.py     # get_client, get_authed_client, get_service_client, get_user_from_token
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Flask test client, auth_headers, test_user, cleanup fixtures
│   ├── test_auth.py        # Register + login tests (written)
│   ├── test_chat.py        # Chat endpoint tests (empty)
│   ├── test_scores.py      # Scores + leaderboard tests (empty)
│   ├── test_challenge.py   # Challenge generate + evaluate tests (empty)
│   └── security/
│       ├── __init__.py
│       ├── test_auth_bypass.py       # Auth bypass attempts (empty)
│       ├── test_rate_limiting.py     # Rate limit enforcement (empty)
│       ├── test_input_validation.py  # Input sanitisation (empty)
│       └── test_rls.py               # RLS policy enforcement (empty)
├── supabase_schema.sql     # Full schema + RLS policies
├── pytest.ini              # pytest config (testpaths = tests)
├── requirements.txt        # Full frozen dependencies
├── .env                    # Secret keys (never commit)
├── .gitignore
└── CLAUDE.md               # This file
```

---

## Database Schema

| Table | Key Columns |
|---|---|
| `users` | `id uuid PK`, `username text UNIQUE NOT NULL`, `email text`, `created_at` |
| `sessions` | `id uuid PK`, `user_id uuid FK`, `topic text`, `started_at` |
| `messages` | `id uuid PK`, `session_id uuid FK`, `role text`, `content text`, `created_at` |
| `challenges` | `id uuid PK`, `session_id uuid FK`, `question text`, `user_answer text`, `correct_answer text`, `correct bool`, `score int` |
| `scores` | `id uuid PK`, `user_id uuid FK`, `total_points int`, `streak int`, `longest_streak int`, `challenges_completed int`, `updated_at` |
| `leaderboard` | View: `username`, `total_points`, `streak`, `rank` |

RLS enabled on all tables. Users can only read/write their own data.
`leaderboard` view is publicly readable (no RLS).

---

## Supabase Client Pattern

Three client types are used:
- `get_client()` — anon key, for auth API calls (sign_up, sign_in)
- `get_authed_client(token)` — anon key + user JWT via `postgrest.auth(token)`, for all RLS-protected DB ops
- `get_service_client()` — service role key (`SUPABASE_SECRET_KEY`), for registration inserts that run before user has a session

---

## API Routes

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/api/users/register` | No | Register new account |
| POST | `/api/users/login` | No | Login, get JWT |
| GET | `/api/users/<user_id>` | Yes | Get user profile |
| POST | `/api/chat` | Yes | Send message, get Socratic response (30/hr) |
| GET | `/api/chat/history` | Yes | Fetch session history |
| POST | `/api/challenge` | Yes | Generate recall challenge (20/hr) |
| POST | `/api/challenge/evaluate` | Yes | Evaluate answer, update scores (20/hr) |
| GET | `/api/scores/<user_id>` | Yes | Get points, streak, rank |
| GET | `/api/leaderboard` | No | Global leaderboard (top 20) |
| GET | `/api/health` | No | Health check |

---

## Environment Variables

```
SUPABASE_URL
SUPABASE_KEY           # anon/publishable key
SUPABASE_SECRET_KEY    # service role key (for registration inserts)
CLAUDE_API_KEY
FLASK_SECRET_KEY
FLASK_ENV
```

---

## Running Locally

```bash
# Backend
source .venv/bin/activate
python -m backend.app
# API available at http://localhost:5001

# Frontend
# Open frontend/index.html with Live Server in VSCode (port 5500)

# Tests
pytest
```

---

## Development Rules

1. Always use `get_authed_client(token)` for DB ops inside authenticated routes
2. Never hardcode secrets — use .env
3. Never expose API keys in error responses
4. Every external call (Supabase, Claude API) must be wrapped in try/except
5. Rate limiting decorators go on every AI-calling route
6. The `limiter` object lives in `backend/limiter.py` — never import it from `app.py`

---## Key Decisions Made
- Email confirmation DISABLED in Supabase (no custom domain for Resend SMTP)
- Using legacy Supabase JWT keys (eyJ... format) NOT the new sb_secret_... format
- SUPABASE_SECRET_KEY must be the legacy service_role JWT from the Legacy tab in Supabase
- pytest installed, conftest.py and test_auth.py written — run with: pytest tests/test_auth.py -v

## Next Steps (in order)
1. Run test_auth.py and fix any failures
2. Write test_chat.py
3. Write test_scores.py  
4. Write test_challenge.py
5. Write security tests
6. Fix error messages (duplicate username/email show raw DB errors to user)
7. Push final test suite to GitHub

## Author
KingJames — Intelligent Systems Course 2026
