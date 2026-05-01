# mindful-bot

A cognitive offload resistance chatbot that challenges you to think before revealing answers. Built with a Socratic AI that guides learning through active recall rather than passive consumption.

**Live demo:** [mindful-bot-three.vercel.app](https://mindful-bot-three.vercel.app)
**API:** [mindful-bot.onrender.com](https://mindful-bot.onrender.com)

---

## Screenshots

> *(Add screenshots here)*

---

## Features

- **Socratic AI** — never gives direct answers; prompts recall and reflection first
- **Recall challenges** — triggered every 3 exchanges, scored 0–10 by an evaluator agent
- **Points & streaks** — earn points for correct recall, track streaks across sessions
- **Global leaderboard** — ranked by total points, updated in real time
- **Progress dashboard** — view score, streak, rank, and recent session topics
- **Session topic detection** — each conversation is automatically labelled by topic
- **Account management** — register, login, update username/email/password, delete account
- **Theme switcher** — Light, Dark, and Deep Space modes

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Animations | AOS (Animate On Scroll) + CSS |
| Backend | Python, Flask, Gunicorn |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (JWT) |
| AI | Anthropic Claude API (`claude-sonnet-4-6`) |
| Rate Limiting | flask-limiter |
| Testing | pytest |
| Hosting | Vercel (frontend), Render (backend) |

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/mindful-bot.git
cd mindful-bot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SECRET_KEY=
CLAUDE_API_KEY=
FLASK_SECRET_KEY=
FLASK_ENV=development
```

See [Environment Variables](#environment-variables) for details on each.

### 4. Run the backend

```bash
python -m backend.app
# API available at http://localhost:5001
```

### 5. Open the frontend

Open `frontend/index.html` with Live Server in VSCode (runs on port 5500).

---

## Environment Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/publishable key |
| `SUPABASE_SECRET_KEY` | Supabase service role key (legacy JWT format, from Legacy API tab) |
| `CLAUDE_API_KEY` | Anthropic API key |
| `FLASK_SECRET_KEY` | Random secret for Flask sessions |
| `FLASK_ENV` | `development` or `production` |

---

## Running Tests

```bash
pytest
```

Tests are in `tests/` and require a live Supabase connection. A unique test user is created and deleted automatically each run.

---

## Project Structure

```
mindful-bot/
├── frontend/           # Static HTML/CSS/JS frontend
│   ├── js/
│   │   ├── config.js   # Dynamic API base URL
│   │   ├── main.js     # Auth, shared utilities
│   │   ├── chat.js     # Chat + challenge flow
│   │   ├── dashboard.js
│   │   └── leaderboard.js
│   └── css/
├── backend/
│   ├── app.py          # Flask entry point
│   ├── limiter.py      # Rate limiter instance
│   ├── agents/
│   │   ├── chatbot.py      # Socratic AI (Agent 1)
│   │   ├── challenger.py   # Recall challenge generator (Agent 2)
│   │   └── evaluator.py    # Answer evaluator (Agent 3)
│   ├── routes/
│   │   ├── chat.py     # /api/chat, /api/challenge
│   │   ├── scores.py   # /api/scores, /api/leaderboard
│   │   └── users.py    # /api/users
│   └── database/
│       └── supabase.py
├── tests/
├── supabase_schema.sql
├── requirements.txt
└── .env
```

---

## Author

KingJames — Intelligent Systems Course 2026
