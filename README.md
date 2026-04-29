# mindful-bot 🧠

> A cognitive offload resistance chatbot that challenges you to think before getting answers.

## Overview

mindful-bot is an AI-powered learning tool that uses the Socratic method to prevent cognitive offload — the tendency to outsource thinking to AI instead of engaging with problems directly. Rather than providing answers on demand, it guides users to reason through questions first, then tests retention with timed recall challenges, and rewards active thinking with a points-based leaderboard system. Built as a full-stack web application for an Intelligent Systems course.

---

## Live Demo

[Add deployment URL here]

---

## Features

- **Socratic AI Chatbot** (Claude claude-sonnet-4-6) — never gives answers directly; guides thinking with Socratic questions before revealing anything
- **Recall Challenge System** — triggers automatically every 3 exchanges, scored 0–10 points by an AI evaluator agent
- **Points & Streak Tracking** — real-time scoring saved to database after every evaluated challenge
- **Global Leaderboard** — all users ranked by total recall points via a live Supabase view
- **Progress Dashboard** — personal stats including total points, streak, global rank, and recent sessions
- **User Authentication** — register, login, and email confirmation via Supabase Auth
- **Settings Page** — update username, email, password, or permanently delete account
- **3 AI Agents** — independent Socratic chatbot, challenge generator, and evaluator with separate system prompts
- **Theme Switcher** — Light, Dark, and Deep Space modes persisted in localStorage
- **3D Animations** — animated water bubble canvas with depth background, glassmorphism cards, and scroll reveal effects
- **Profile Dropdown** — avatar initial, quick navigation links, and sign out
- **Responsive Design** — works on desktop and mobile

---

## Tech Stack

### Frontend
- HTML, CSS, Vanilla JavaScript
- Supabase JS Client (auth + direct DB queries for sessions and leaderboard)
- AOS (Animate On Scroll)
- Canvas API for animated bubble + depth background effects
- Custom CSS glassmorphism, 3D tilt cards, and scroll reveal

### Backend
- Python Flask (REST API on port 5001)
- Anthropic Claude API (`claude-sonnet-4-6`)
  - **Agent 1:** Socratic chatbot — warm, Socratic system prompt; never answers directly
  - **Agent 2:** Recall challenge generator — produces targeted questions from conversation context
  - **Agent 3:** Challenge evaluator — scores 0–10, gives feedback, returns structured JSON
- Supabase Python client with per-request JWT authentication

### Database
- Supabase (PostgreSQL)
- Tables: `users`, `sessions`, `messages`, `challenges`, `scores`
- Row Level Security (RLS) on all tables — `auth.uid()` policies enforce user data isolation
- `leaderboard` view with `RANK() OVER` for real-time global rankings

### Auth
- Supabase Auth (email + password)
- JWT tokens passed from frontend → Flask → Supabase PostgREST for all authenticated DB operations

---

## Database Schema

| Table | Key Columns |
|---|---|
| `users` | `id`, `username`, `email`, `created_at` |
| `sessions` | `id`, `user_id`, `topic`, `started_at` |
| `messages` | `id`, `session_id`, `role`, `content`, `created_at` |
| `challenges` | `id`, `session_id`, `question`, `user_answer`, `correct_answer`, `correct`, `score` |
| `scores` | `id`, `user_id`, `total_points`, `streak`, `longest_streak`, `challenges_completed`, `updated_at` |
| `leaderboard` | View: `username`, `total_points`, `streak`, `rank` |

RLS is enabled on all tables. Users can only read and write their own data. The `leaderboard` view is publicly readable with no RLS.

---

## Security

- Row Level Security (RLS) on all Supabase tables with `auth.uid() = user_id` policies
- JWT token passed from frontend → Flask → Supabase PostgREST via `client.postgrest.auth(token)` so `auth.uid()` resolves correctly on every request
- Password hashing handled entirely by Supabase Auth
- Input validation on all form fields (frontend and backend)
- Environment variables for all secrets — never committed to version control

---

## Project Structure

```
mindful-bot/
├── frontend/
│   ├── index.html        # Landing page with 3D animations
│   ├── chat.html         # Main chat interface
│   ├── dashboard.html    # User progress dashboard
│   ├── leaderboard.html  # Global rankings
│   ├── settings.html     # Account settings
│   ├── css/
│   │   └── main.css      # Design system + components
│   └── js/
│       ├── config.js     # Supabase + API config
│       ├── main.js       # Shared auth + utilities
│       ├── chat.js       # Chat + challenge logic
│       ├── dashboard.js  # Dashboard data fetching
│       └── leaderboard.js# Leaderboard rendering
├── backend/
│   ├── app.py            # Flask app entry point
│   ├── agents/
│   │   ├── chatbot.py    # Socratic chatbot agent
│   │   ├── challenger.py # Recall challenge generator
│   │   └── evaluator.py  # Challenge evaluator + scorer
│   ├── routes/
│   │   ├── chat.py       # Chat, challenge, evaluate endpoints
│   │   ├── users.py      # User profile endpoints
│   │   └── scores.py     # Score + leaderboard endpoints
│   └── database/
│       └── supabase.py   # Supabase client + authed client
├── supabase_schema.sql   # Full schema + RLS policies
├── requirements.txt
├── .env                  # Environment variables (not committed)
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- A [Supabase](https://supabase.com) project with the schema applied
- An [Anthropic](https://console.anthropic.com) API key

### Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
CLAUDE_API_KEY=your_anthropic_api_key
FLASK_SECRET_KEY=any_random_secret_string
FLASK_ENV=development
```

### Running Locally

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mindful-bot.git
cd mindful-bot

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database schema
# Open Supabase dashboard → SQL Editor → run supabase_schema.sql

# 5. Start Flask backend
python -m backend.app
# API available at http://localhost:5001

# 6. Open frontend
# Open frontend/index.html with Live Server in VS Code (port 5500)
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/users/register` | No | Create new account |
| `POST` | `/api/users/login` | No | Authenticate, get JWT |
| `GET` | `/api/users/<user_id>` | Yes | Get user profile |
| `POST` | `/api/chat` | Yes | Send message, get Socratic response |
| `GET` | `/api/chat/history` | Yes | Fetch session message history |
| `POST` | `/api/challenge` | Yes | Generate recall challenge from conversation |
| `POST` | `/api/challenge/evaluate` | Yes | Evaluate answer, update scores |
| `GET` | `/api/scores/<user_id>` | Yes | Get user points, streak, and rank |
| `GET` | `/api/leaderboard` | No | Get global leaderboard |

All protected routes require `Authorization: Bearer <token>` header.

---

## Testing

- RLS policies verified on all tables — queries fail correctly without valid JWT
- JWT authentication enforced on all protected routes
- Challenge triggers confirmed at every 3rd user exchange
- Score calculation, streak increment, and longest streak tracking verified
- Settings CRUD operations tested (username, email, password, delete)
- Cross-theme rendering verified (Light / Dark / Deep Space)
- Auth guard on protected pages (chat, dashboard, settings, leaderboard)

---

## Known Limitations

- Sessions all show "General conversation" as topic — automatic topic detection not yet implemented
- No pagination on leaderboard — renders all users
- No mobile-optimised chat keyboard handling

---

## Author

KingJames — Intelligent Systems Course 2026

---

## License

MIT
